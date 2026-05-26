"""backend → payment-svc HTTP 클라이언트.

payment-svc 측 dto/internal.py 와 동일한 schema 가 본 모듈 내부에 자체 정의된다. 
계약 변경 시 양쪽을 같이 수정.
"""
from typing import Optional
from pydantic import BaseModel
import httpx

from app.core.logger import get_logger
from app.config.setting import settings

logger = get_logger("internal_client.payment")


# ───────── payment-svc 측 dto 와 매칭 ─────────


class StorePaymentInfoDTO(BaseModel):
    store_id: str
    portone_store_id: Optional[str] = None
    portone_channel_id: Optional[str] = None
    portone_secret_key: Optional[str] = None


# ───────── 예외 ─────────


class PaymentServiceError(Exception):
    """payment-svc 응답이 비-2xx 일 때 (4xx/5xx 모두). status_code 와 detail 보존."""

    def __init__(self, status_code: int, detail: str):
        super().__init__(f"payment-svc {status_code}: {detail}")
        self.status_code = status_code
        self.detail = detail


class PaymentServiceUnavailableError(PaymentServiceError):
    """5xx / 네트워크 — caller 가 transient 로 처리할 수 있다."""


# ───────── client ─────────


class InternalPaymentClient:
    """payment-svc internal API wrapper. stateless — Singleton."""

    def __init__(self, *, timeout_s: float = 5.0):
        self._client = httpx.AsyncClient(
            base_url=settings.PAYMENT_SERVICE_URL,
            timeout=timeout_s,
            headers={"X-Internal-Token": settings.INTERNAL_SERVICE_TOKEN},
        )


    async def close(self) -> None:
        await self._client.aclose()


    async def get_store_payment_info(
        self, store_id: str,
    ) -> Optional[StorePaymentInfoDTO]:
        """완전한 결제 정보. 없거나 불완전이면 None."""
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


    async def has_complete_info(self, store_id: str) -> bool:
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


    async def exists_info(self, store_id: str) -> bool:
        """row 존재 여부 (완전성 무관). 1차 가입의 register 충돌 회피용."""
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


    async def delete_store_payment_info(self, store_id: str) -> None:
        """seller 탈퇴 cleanup. 없어도 204 (멱등)."""
        try:
            resp = await self._client.delete(
                f"/api/internal/payment/store-info/{store_id}",
            )
        except httpx.HTTPError as e:
            raise PaymentServiceUnavailableError(503, str(e)) from e

        if resp.status_code in (200, 204):
            return
        if 500 <= resp.status_code < 600:
            raise PaymentServiceUnavailableError(resp.status_code, resp.text[:200])
        raise PaymentServiceError(resp.status_code, resp.text[:200])


    async def register_store_payment_info(
        self,
        *,
        store_id: str,
        portone_store_id: str,
        portone_channel_id: str,
        portone_secret_key: str,
    ) -> None:
        """가게 1차 등록. 이미 있으면 409 raise (caller 가 처리)."""
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


    async def refund(
        self, *, payment_id: str, store_id: str, reason: str,
    ) -> None:
        """PortOne refund 트리거. payment-svc 가 자체 secret_key 로 호출.

        Raises:
            PaymentServiceError(400): 가게 결제 설정 누락.
            PaymentServiceError(500): refund 자체 실패 — caller 가 critical 로깅.
            PaymentServiceUnavailableError: 5xx / 네트워크.
        """
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
