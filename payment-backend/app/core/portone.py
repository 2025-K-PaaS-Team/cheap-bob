"""PortOne v2 REST API client.

용도:
  - confirm 단계의 server-side verify — `GET /payments/{paymentId}` 로 결제 진실 재조회.
  - 취소/환불 — `POST /payments/{paymentId}/cancel`.

인증 (https://developers.portone.io/api/rest-v2):
  `Authorization: PortOne {V2_API_SECRET}` — store 별로 발급되어 `store_payment_info` 에 저장.

graceful 실패 정책:
  - 404 / 4xx           → `PortOnePaymentNotFoundError` (claim 거부)
  - 5xx / timeout / 네트워크 → `PortOneTransientError` (caller 가 일시 장애로 인지)
  - HTTPException 은 본 모듈에서 raise 하지 않는다 — CONVENTION §11. router 에서 변환.
"""
from typing import Any, Optional
import httpx
from enum import Enum
from dataclasses import dataclass

from app.core.logger import get_logger


logger = get_logger("core.portone")


class PortOnePaymentNotFoundError(Exception):
    """PortOne 측에 해당 paymentId 없음 또는 4xx — claim 거부."""


class PortOneTransientError(Exception):
    """일시 장애 (5xx / timeout / 네트워크). caller 가 재시도 가능."""


class PortOnePaymentStatus(str, Enum):
    READY = "READY"
    PENDING = "PENDING"
    VIRTUAL_ACCOUNT_ISSUED = "VIRTUAL_ACCOUNT_ISSUED"
    PAID = "PAID"
    FAILED = "FAILED"
    PARTIAL_CANCELLED = "PARTIAL_CANCELLED"
    CANCELLED = "CANCELLED"


@dataclass(frozen=True)
class PortOnePayment:
    """`GET /payments/{paymentId}` 응답에서 verifier 가 쓰는 필드만 추출."""

    payment_id: str
    status: PortOnePaymentStatus
    total_amount: int
    currency: str
    order_name: Optional[str]
    payment_method: Optional[str]
    store_id: Optional[str]


class PortOnePaymentClient:
    """PortOne v2 결제 조회/취소 client.

    stateless — 호출마다 api_secret 주입. AsyncClient 는 reuse 해서 connection pool 공유.
    Singleton 으로 컨테이너에 등록하고 lifespan 종료 시 close() 호출.
    """

    def __init__(
        self,
        *,
        base_url: str = "https://api.portone.io",
        timeout_s: float = 3.0,
    ):
        self._client = httpx.AsyncClient(base_url=base_url, timeout=timeout_s)


    async def close(self) -> None:
        await self._client.aclose()


    async def fetch_payment(
        self, payment_id: str, *, api_secret: str,
    ) -> PortOnePayment:
        """Raises: PortOnePaymentNotFoundError (4xx), PortOneTransientError (5xx/network)."""
        url = f"/payments/{payment_id}"
        try:
            resp = await self._client.get(
                url, headers={"Authorization": f"PortOne {api_secret}"},
            )
        except httpx.HTTPError as e:
            logger.warning(
                "PortOne fetch_payment 네트워크 실패 payment_id={}: {}", payment_id, e,
            )
            raise PortOneTransientError(str(e)) from e

        if 500 <= resp.status_code < 600:
            raise PortOneTransientError(
                f"PortOne 5xx (status={resp.status_code} payment_id={payment_id})",
            )
        if resp.status_code >= 400:
            raise PortOnePaymentNotFoundError(
                f"PortOne {resp.status_code} (payment_id={payment_id})",
            )

        try:
            data = resp.json()
        except ValueError as e:
            raise PortOnePaymentNotFoundError(
                f"PortOne 응답 JSON 파싱 실패: {e}",
            ) from e
        return _parse_payment(data, payment_id)


    async def cancel_payment(
        self, payment_id: str, *, api_secret: str, reason: str,
    ) -> dict[str, Any]:
        """Raises: PortOnePaymentNotFoundError (4xx), PortOneTransientError (5xx/network)."""
        url = f"/payments/{payment_id}/cancel"
        try:
            resp = await self._client.post(
                url,
                headers={"Authorization": f"PortOne {api_secret}"},
                json={"reason": reason},
            )
        except httpx.HTTPError as e:
            logger.warning(
                "PortOne cancel_payment 네트워크 실패 payment_id={}: {}", payment_id, e,
            )
            raise PortOneTransientError(str(e)) from e

        if 500 <= resp.status_code < 600:
            raise PortOneTransientError(
                f"PortOne cancel 5xx (status={resp.status_code} payment_id={payment_id})",
            )
        if resp.status_code >= 400:
            raise PortOnePaymentNotFoundError(
                f"PortOne cancel {resp.status_code} (payment_id={payment_id})",
            )

        try:
            return resp.json()
        except ValueError:
            return {"status": "success", "payment_id": payment_id}


def _parse_payment(data: dict[str, Any], expected_payment_id: str) -> PortOnePayment:
    try:
        payment_id = data["id"]
        status_str = data["status"]
        amount = data["amount"]["total"]
        currency = data["currency"]
    except (KeyError, TypeError) as e:
        raise PortOnePaymentNotFoundError(
            f"PortOne 응답 필수 필드 누락: {e}",
        ) from e

    if payment_id != expected_payment_id:
        raise PortOnePaymentNotFoundError(
            f"PortOne 응답 paymentId 불일치 expected={expected_payment_id} got={payment_id}",
        )

    try:
        status = PortOnePaymentStatus(status_str)
    except ValueError as e:
        raise PortOnePaymentNotFoundError(
            f"알 수 없는 PortOne 상태: {status_str}",
        ) from e

    if not isinstance(amount, int):
        raise PortOnePaymentNotFoundError(
            f"PortOne amount.total 타입 오류: {type(amount).__name__}",
        )

    store_id = None
    if isinstance(data.get("storeId"), str):
        store_id = data["storeId"]
    elif isinstance(data.get("store"), dict):
        store_id = data["store"].get("id")

    return PortOnePayment(
        payment_id=payment_id,
        status=status,
        total_amount=amount,
        currency=currency,
        order_name=data.get("orderName"),
        payment_method=_extract_method(data.get("method")),
        store_id=store_id,
    )


def _extract_method(method: Any) -> Optional[str]:
    if method is None:
        return None
    if isinstance(method, str):
        return method
    if isinstance(method, dict):
        return method.get("type") or method.get("name")
    return str(method)
