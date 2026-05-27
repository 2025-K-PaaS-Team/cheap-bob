"""payment-backend → main-backend.order HTTP 클라이언트.

Resilience:
  - timeout (httpx.Timeout)
  - CircuitBreaker — BackendUnavailableError 누적 시 OPEN.
                    OrderCreateFailedError (4xx) 는 breaker 영향 없음 — 비즈니스 실패 신호.
  - retry_with_backoff — 5xx/네트워크만 재시도. OrderCreateFailedError, CircuitBreakerOpenError 즉시 raise.

멱등성: backend 의 create_order_from_cart 가 payment_id 기준 UNIQUE 멱등. retry 안전.
"""
from typing import Awaitable, Callable, Optional, TypeVar
import httpx

from app.domain.payment.service.exception import (
    BackendUnavailableError,
    OrderCreateFailedError,
)
from app.domain.payment.dto.internal import CreateOrderFromCartRequest
from app.core.resilience import (
    CircuitBreaker,
    CircuitBreakerOpenError,
    retry_with_backoff,
)
from app.core.logger import get_logger
from app.config.setting import settings


logger = get_logger("internal_client.order")

T = TypeVar("T")


class InternalOrderClient:
    """order 도메인 internal API. stateless — Singleton."""

    def __init__(self, *, timeout_s: float = 5.0):
        self._client = httpx.AsyncClient(
            base_url=settings.BACKEND_SERVICE_URL,
            timeout=timeout_s,
            headers={"X-Internal-Token": settings.INTERNAL_SERVICE_TOKEN},
        )
        self._breaker = CircuitBreaker(
            name="main-backend:order",
            failure_threshold=settings.CB_FAILURE_THRESHOLD,
            recovery_timeout=settings.CB_RECOVERY_TIMEOUT_SEC,
            expected_exception=BackendUnavailableError,
        )


    @property
    def breaker(self) -> CircuitBreaker:
        return self._breaker


    async def close(self) -> None:
        await self._client.aclose()


    async def _resilient(self, do_call: Callable[[], Awaitable[T]]) -> T:
        async def _attempt() -> T:
            return await self._breaker.call(do_call)

        return await retry_with_backoff(
            _attempt,
            max_attempts=settings.RETRY_MAX_ATTEMPTS,
            base_delay_ms=settings.RETRY_BASE_DELAY_MS,
            retriable=(BackendUnavailableError,),
            do_not_retry=(CircuitBreakerOpenError, OrderCreateFailedError),
        )


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
        """payment_id UNIQUE 멱등 — retry 안전.

        Raises:
            OrderCreateFailedError: main-backend 4xx (validation 등).
            BackendUnavailableError: 5xx / 네트워크 (retry 소진 후 raise).
        """
        await self._resilient(lambda: self._do_create_order_from_cart(
            payment_id=payment_id,
            product_id=product_id,
            customer_id=customer_id,
            quantity=quantity,
            price=price,
            sale=sale,
            total_amount=total_amount,
        ))


    async def _do_create_order_from_cart(
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
            raise BackendUnavailableError(f"main-backend 호출 실패: {e}") from e

        if resp.status_code in (200, 201, 204):
            return
        if 500 <= resp.status_code < 600:
            raise BackendUnavailableError(
                f"main-backend 5xx (status={resp.status_code})",
            )
        # 4xx — finalize 가 보상 트리거를 돌릴 신호.
        raise OrderCreateFailedError(
            f"main-backend order 생성 실패 (status={resp.status_code}): {resp.text[:200]}",
        )
