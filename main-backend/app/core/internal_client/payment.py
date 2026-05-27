"""main-backend → payment-backend HTTP 클라이언트.

payment-backend 측 dto/internal.py 와 동일한 schema 가 본 모듈 내부에 자체 정의된다.
계약 변경 시 양쪽을 같이 수정.

Resilience:
  - timeout (httpx.Timeout)
  - CircuitBreaker — 누적 PaymentServiceUnavailableError 가 임계치 초과 시 OPEN.
                    4xx (PaymentServiceError) 는 breaker 영향 없음 — caller 책임 신호.
  - retry_with_backoff — 5xx/네트워크만 재시도. 4xx, CircuitBreakerOpenError 는 즉시 raise.
"""
from typing import Awaitable, Callable, Optional, TypeVar
from pydantic import BaseModel
import httpx

from app.core.resilience import (
    CircuitBreaker,
    CircuitBreakerOpenError,
    retry_with_backoff,
)
from app.core.logger import get_logger
from app.config.setting import settings


logger = get_logger("internal_client.payment")

T = TypeVar("T")


# ───────── payment-backend 측 dto 와 매칭 ─────────


class StorePaymentInfoDTO(BaseModel):
    store_id: str
    portone_store_id: Optional[str] = None
    portone_channel_id: Optional[str] = None
    portone_secret_key: Optional[str] = None


# ───────── 예외 ─────────


class PaymentServiceError(Exception):
    """payment-backend 응답이 비-2xx 일 때 (4xx). caller 책임 신호 — breaker 영향 없음."""

    def __init__(self, status_code: int, detail: str):
        super().__init__(f"payment-backend {status_code}: {detail}")
        self.status_code = status_code
        self.detail = detail


class PaymentServiceUnavailableError(PaymentServiceError):
    """5xx / 네트워크 — transient. breaker trip + retry 대상."""


# ───────── client ─────────


class InternalPaymentClient:
    """payment-backend internal API wrapper. stateless — Singleton."""

    def __init__(self, *, timeout_s: float = 5.0):
        self._client = httpx.AsyncClient(
            base_url=settings.PAYMENT_SERVICE_URL,
            timeout=timeout_s,
            headers={"X-Internal-Token": settings.INTERNAL_SERVICE_TOKEN},
        )
        # 단일 회로 — payment-backend 라는 한 외부 의존성에 대한 상태.
        self._breaker = CircuitBreaker(
            name="payment-backend",
            failure_threshold=settings.CB_FAILURE_THRESHOLD,
            recovery_timeout=settings.CB_RECOVERY_TIMEOUT_SEC,
            expected_exception=PaymentServiceUnavailableError,
        )


    @property
    def breaker(self) -> CircuitBreaker:
        """health endpoint 에서 state 노출용."""
        return self._breaker


    async def close(self) -> None:
        await self._client.aclose()


    async def _resilient(self, do_call: Callable[[], Awaitable[T]]) -> T:
        """모든 메서드 공통 wrap — breaker + retry. 4xx 는 do_not_retry."""
        async def _attempt() -> T:
            return await self._breaker.call(do_call)

        return await retry_with_backoff(
            _attempt,
            max_attempts=settings.RETRY_MAX_ATTEMPTS,
            base_delay_ms=settings.RETRY_BASE_DELAY_MS,
            retriable=(PaymentServiceUnavailableError,),
            do_not_retry=(CircuitBreakerOpenError, PaymentServiceError),
        )


    # ───────── public API ─────────


    async def get_store_payment_info(
        self, store_id: str,
    ) -> Optional[StorePaymentInfoDTO]:
        """완전한 결제 정보. 없거나 불완전이면 None."""
        return await self._resilient(lambda: self._do_get_store_payment_info(store_id))


    async def has_complete_info(self, store_id: str) -> bool:
        return await self._resilient(lambda: self._do_has_complete_info(store_id))


    async def exists_info(self, store_id: str) -> bool:
        """row 존재 여부 (완전성 무관). 1차 가입의 register 충돌 회피용."""
        return await self._resilient(lambda: self._do_exists_info(store_id))


    async def register_store_payment_info(
        self,
        *,
        store_id: str,
        portone_store_id: str,
        portone_channel_id: str,
        portone_secret_key: str,
    ) -> None:
        """가게 1차 등록. 이미 있으면 409 raise (caller 가 처리)."""
        await self._resilient(lambda: self._do_register_store_payment_info(
            store_id=store_id,
            portone_store_id=portone_store_id,
            portone_channel_id=portone_channel_id,
            portone_secret_key=portone_secret_key,
        ))


    async def refund(
        self, *, payment_id: str, store_id: str, reason: str,
    ) -> None:
        """PortOne refund 트리거. payment-backend 가 자체 secret_key 로 호출.

        Raises:
            PaymentServiceError(400): 가게 결제 설정 누락.
            PaymentServiceError(500): refund 자체 실패 — caller 가 critical 로깅.
            PaymentServiceUnavailableError: 5xx / 네트워크 (transient — retry 후 raise).
        """
        await self._resilient(lambda: self._do_refund(
            payment_id=payment_id, store_id=store_id, reason=reason,
        ))


    # ───────── private — 실제 HTTP 호출 ─────────


    async def _do_get_store_payment_info(
        self, store_id: str,
    ) -> Optional[StorePaymentInfoDTO]:
        try:
            resp = await self._client.get(
                f"/api/internal/payment/store-info/{store_id}",
            )
        except httpx.HTTPError as e:
            logger.warning("get_store_payment_info 네트워크 오류 store_id={}: {}", store_id, e)
            raise PaymentServiceUnavailableError(503, str(e)) from e

        if resp.status_code == 200:
            return StorePaymentInfoDTO.model_validate(resp.json())
        if resp.status_code == 404:
            return None
        if 500 <= resp.status_code < 600:
            raise PaymentServiceUnavailableError(resp.status_code, resp.text[:200])
        raise PaymentServiceError(resp.status_code, resp.text[:200])


    async def _do_has_complete_info(self, store_id: str) -> bool:
        try:
            resp = await self._client.get(
                f"/api/internal/payment/store-info/{store_id}/has-complete",
            )
        except httpx.HTTPError as e:
            raise PaymentServiceUnavailableError(503, str(e)) from e

        if resp.status_code == 200:
            return resp.json().get("has_complete", False)
        if 500 <= resp.status_code < 600:
            raise PaymentServiceUnavailableError(resp.status_code, resp.text[:200])
        raise PaymentServiceError(resp.status_code, resp.text[:200])


    async def _do_exists_info(self, store_id: str) -> bool:
        try:
            resp = await self._client.get(
                f"/api/internal/payment/store-info/{store_id}/exists",
            )
        except httpx.HTTPError as e:
            raise PaymentServiceUnavailableError(503, str(e)) from e

        if resp.status_code == 200:
            return resp.json().get("exists", False)
        if 500 <= resp.status_code < 600:
            raise PaymentServiceUnavailableError(resp.status_code, resp.text[:200])
        raise PaymentServiceError(resp.status_code, resp.text[:200])


    async def _do_register_store_payment_info(
        self,
        *,
        store_id: str,
        portone_store_id: str,
        portone_channel_id: str,
        portone_secret_key: str,
    ) -> None:
        body = {
            "store_id": store_id,
            "portone_store_id": portone_store_id,
            "portone_channel_id": portone_channel_id,
            "portone_secret_key": portone_secret_key,
        }
        try:
            resp = await self._client.post(
                "/api/internal/payment/store-info", json=body,
            )
        except httpx.HTTPError as e:
            raise PaymentServiceUnavailableError(503, str(e)) from e

        if resp.status_code in (200, 204):
            return
        if 500 <= resp.status_code < 600:
            raise PaymentServiceUnavailableError(resp.status_code, resp.text[:200])
        raise PaymentServiceError(resp.status_code, resp.text[:200])


    async def _do_refund(
        self, *, payment_id: str, store_id: str, reason: str,
    ) -> None:
        body = {"payment_id": payment_id, "store_id": store_id, "reason": reason}
        try:
            resp = await self._client.post(
                "/api/internal/payment/refund", json=body,
            )
        except httpx.HTTPError as e:
            raise PaymentServiceUnavailableError(503, str(e)) from e

        if resp.status_code in (200, 204):
            return
        if 500 <= resp.status_code < 600:
            raise PaymentServiceUnavailableError(resp.status_code, _detail(resp))
        raise PaymentServiceError(resp.status_code, _detail(resp))


def _detail(resp: httpx.Response) -> str:
    try:
        d = resp.json().get("detail")
        return d if isinstance(d, str) else resp.text[:200]
    except (ValueError, AttributeError):
        return resp.text[:200]
