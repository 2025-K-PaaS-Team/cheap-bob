"""payment-backend → main-backend.seller HTTP 클라이언트.

main-backend 의 /api/internal/seller/* 를 호출. X-Internal-Token 헤더로 인증.
실패 시 stock/operation 별 도메인 예외로 매핑.

Resilience:
  - timeout (httpx.Timeout)
  - CircuitBreaker — BackendUnavailableError 누적 시 OPEN. 도메인 예외는 breaker 영향 없음.
  - retry_with_backoff — 5xx/네트워크만 재시도. 도메인 4xx 는 즉시 raise.
"""
from typing import Awaitable, Callable, Optional, TypeVar
import httpx

from app.domain.payment.service.exception import (
    BackendUnavailableError,
    ProductNotFoundError,
    StockConflictError,
    StockInsufficientError,
    StoreNotFoundError,
)
from app.domain.payment.dto.internal import (
    ConsumeStockRequest,
    ProductResponse,
    RestoreStockRequest,
    TodayOperationResponse,
)
from app.core.resilience import (
    CircuitBreaker,
    CircuitBreakerOpenError,
    retry_with_backoff,
)
from app.core.logger import get_logger
from app.config.setting import settings


logger = get_logger("internal_client.seller")

T = TypeVar("T")


class InternalSellerClient:
    """seller 도메인 internal API 호출 wrapper. stateless — Singleton OK."""

    def __init__(self, *, timeout_s: float = 5.0):
        self._client = httpx.AsyncClient(
            base_url=settings.BACKEND_SERVICE_URL,
            timeout=timeout_s,
            headers={"X-Internal-Token": settings.INTERNAL_SERVICE_TOKEN},
        )
        self._breaker = CircuitBreaker(
            name="main-backend:seller",
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
            do_not_retry=(
                CircuitBreakerOpenError,
                # 도메인 4xx — retry 가 결과를 바꾸지 못함.
                StockInsufficientError,
                StockConflictError,
                ProductNotFoundError,
                StoreNotFoundError,
            ),
        )


    # ───────── public API ─────────


    async def find_product(self, product_id: str) -> Optional[ProductResponse]:
        return await self._resilient(lambda: self._do_find_product(product_id))


    async def get_today_operation(self, store_id: str) -> Optional[TodayOperationResponse]:
        return await self._resilient(lambda: self._do_get_today_operation(store_id))


    async def consume_stock(
        self, *, payment_id: str, product_id: str, quantity: int,
    ) -> None:
        """(payment_id, "consume") 단위로 진짜 멱등 — backend 의 stock_operation_log INSERT
        ON CONFLICT DO NOTHING 이 같은 키의 재호출을 SQL 레벨에서 차단한다. retry 안전.

        Raises:
            StockInsufficientError: 재고 부족 (HTTP 400).
            StockConflictError:     낙관적 락 충돌 (HTTP 409).
            BackendUnavailableError: 그 외 5xx / 네트워크.
        """
        await self._resilient(lambda: self._do_consume_stock(
            payment_id=payment_id, product_id=product_id, quantity=quantity,
        ))


    async def restore_stock(
        self, *, payment_id: str, product_id: str, quantity: int,
    ) -> None:
        """(payment_id, "restore") 단위로 진짜 멱등."""
        await self._resilient(lambda: self._do_restore_stock(
            payment_id=payment_id, product_id=product_id, quantity=quantity,
        ))


    async def get_store_id_by_seller_email(self, seller_email: str) -> str:
        """seller_email → store_id."""
        return await self._resilient(
            lambda: self._do_get_store_id_by_seller_email(seller_email),
        )


    # ───────── private — 실제 HTTP 호출 ─────────


    async def _do_find_product(self, product_id: str) -> Optional[ProductResponse]:
        try:
            resp = await self._client.get(
                f"/api/internal/seller/products/{product_id}",
            )
        except httpx.HTTPError as e:
            logger.warning("find_product 네트워크 오류 product_id={}: {}", product_id, e)
            raise BackendUnavailableError(f"main-backend 호출 실패: {e}") from e

        if resp.status_code == 404:
            return None
        if 500 <= resp.status_code < 600:
            raise BackendUnavailableError(
                f"main-backend 5xx (status={resp.status_code} product_id={product_id})",
            )
        if resp.status_code >= 400:
            raise BackendUnavailableError(
                f"main-backend {resp.status_code}: {resp.text[:200]}",
            )
        return ProductResponse.model_validate(resp.json())


    async def _do_get_today_operation(
        self, store_id: str,
    ) -> Optional[TodayOperationResponse]:
        try:
            resp = await self._client.get(
                f"/api/internal/seller/stores/{store_id}/today-operation",
            )
        except httpx.HTTPError as e:
            logger.warning(
                "get_today_operation 네트워크 오류 store_id={}: {}", store_id, e,
            )
            raise BackendUnavailableError(f"main-backend 호출 실패: {e}") from e

        if resp.status_code == 404:
            return None
        if 500 <= resp.status_code < 600:
            raise BackendUnavailableError(
                f"main-backend 5xx (status={resp.status_code} store_id={store_id})",
            )
        if resp.status_code >= 400:
            raise BackendUnavailableError(
                f"main-backend {resp.status_code}: {resp.text[:200]}",
            )
        return TodayOperationResponse.model_validate(resp.json())


    async def _do_consume_stock(
        self, *, payment_id: str, product_id: str, quantity: int,
    ) -> None:
        body = ConsumeStockRequest(
            payment_id=payment_id, product_id=product_id, quantity=quantity,
        )
        try:
            resp = await self._client.post(
                f"/api/internal/seller/products/{product_id}/consume-stock",
                json=body.model_dump(),
            )
        except httpx.HTTPError as e:
            logger.warning("consume_stock 네트워크 오류 payment_id={}: {}", payment_id, e)
            raise BackendUnavailableError(f"main-backend 호출 실패: {e}") from e

        if resp.status_code in (200, 204):
            return
        if resp.status_code == 400:
            raise StockInsufficientError(_extract_detail(resp) or "재고가 부족합니다")
        if resp.status_code == 404:
            raise ProductNotFoundError(_extract_detail(resp) or "상품을 찾을 수 없습니다")
        if resp.status_code == 409:
            raise StockConflictError(_extract_detail(resp) or "재고 변경 중 충돌이 발생했습니다")
        if 500 <= resp.status_code < 600:
            raise BackendUnavailableError(
                f"main-backend 5xx (status={resp.status_code})",
            )
        raise BackendUnavailableError(
            f"main-backend {resp.status_code}: {resp.text[:200]}",
        )


    async def _do_restore_stock(
        self, *, payment_id: str, product_id: str, quantity: int,
    ) -> None:
        body = RestoreStockRequest(
            payment_id=payment_id, product_id=product_id, quantity=quantity,
        )
        try:
            resp = await self._client.post(
                f"/api/internal/seller/products/{product_id}/restore-stock",
                json=body.model_dump(),
            )
        except httpx.HTTPError as e:
            logger.warning("restore_stock 네트워크 오류 payment_id={}: {}", payment_id, e)
            raise BackendUnavailableError(f"main-backend 호출 실패: {e}") from e

        if resp.status_code in (200, 204):
            return
        if resp.status_code == 400:
            raise StockInsufficientError(
                _extract_detail(resp) or "복원 수량이 누계 차감을 초과합니다",
            )
        if resp.status_code == 409:
            raise StockConflictError(
                _extract_detail(resp) or "재고 변경 중 충돌이 발생했습니다",
            )
        if 500 <= resp.status_code < 600:
            raise BackendUnavailableError(
                f"main-backend 5xx (status={resp.status_code})",
            )
        raise BackendUnavailableError(
            f"main-backend {resp.status_code}: {resp.text[:200]}",
        )


    async def _do_get_store_id_by_seller_email(self, seller_email: str) -> str:
        try:
            resp = await self._client.get(
                "/api/internal/seller/store-id",
                params={"seller_email": seller_email},
            )
        except httpx.HTTPError as e:
            raise BackendUnavailableError(f"main-backend 호출 실패: {e}") from e

        if resp.status_code == 200:
            return resp.json()["store_id"]
        if resp.status_code == 404:
            raise StoreNotFoundError("가게를 찾을 수 없습니다")
        raise BackendUnavailableError(
            f"main-backend {resp.status_code}: {resp.text[:200]}",
        )


def _extract_detail(resp: httpx.Response) -> Optional[str]:
    try:
        return resp.json().get("detail")
    except (ValueError, AttributeError):
        return None
