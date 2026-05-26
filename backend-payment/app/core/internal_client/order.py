"""payment-svc → backend.order HTTP 클라이언트."""
from typing import Optional

import httpx

from app.domain.payment.service.exception import (
    BackendUnavailableError,
    OrderCreateFailedError,
)
from app.domain.payment.dto.internal import CreateOrderFromCartRequest
from app.core.logger import get_logger
from app.config.setting import settings


logger = get_logger("internal_client.order")


class InternalOrderClient:
    """order 도메인 internal API. stateless — Singleton."""

    def __init__(self, *, timeout_s: float = 5.0):
        self._client = httpx.AsyncClient(
            base_url=settings.BACKEND_SERVICE_URL,
            timeout=timeout_s,
            headers={"X-Internal-Token": settings.INTERNAL_SERVICE_TOKEN},
        )


    async def close(self) -> None:
        await self._client.aclose()


    async def create_order_from_cart(
        self,
        *,
        payment_id: str,
        product_id: str,
        customer_id: str,
        quantity: int,
        price: int,
        sale: Optional[int],
        total_amount: int,
    ) -> None:
        """backend 가 customer preference snapshot 을 자체 lookup 후 order_current_item 생성.

        payment_id 가 UNIQUE 멱등 키 — 두 번째 호출은 noop (200/204).

        Raises:
            OrderCreateFailedError: backend 가 4xx 비-멱등 오류 (validation 등) 반환.
            BackendUnavailableError: 5xx / 네트워크.
        """
        body = CreateOrderFromCartRequest(
            payment_id=payment_id,
            product_id=product_id,
            customer_id=customer_id,
            quantity=quantity,
            price=price,
            sale=sale,
            total_amount=total_amount,
        )
        try:
            resp = await self._client.post(
                "/api/internal/order/orders/from-cart",
                json=body.model_dump(),
            )
        except httpx.HTTPError as e:
            logger.warning("create_order_from_cart 네트워크 오류 payment_id={}: {}", payment_id, e)
            raise BackendUnavailableError(f"backend 호출 실패: {e}") from e

        if resp.status_code in (200, 201, 204):
            return
        if 500 <= resp.status_code < 600:
            raise BackendUnavailableError(
                f"backend 5xx (status={resp.status_code})",
            )
        # 4xx — finalize 가 보상 트리거를 돌릴 신호.
        raise OrderCreateFailedError(
            f"backend order 생성 실패 (status={resp.status_code}): {resp.text[:200]}",
        )
