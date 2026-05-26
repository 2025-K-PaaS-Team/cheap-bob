"""payment-svc → backend.seller HTTP 클라이언트.

backend 의 /api/internal/seller/* 를 호출. X-Internal-Token 헤더로 인증.
실패 시 stock/operation 별 도메인 예외로 매핑.
"""
from typing import Optional

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
from app.core.logger import get_logger
from app.config.setting import settings


logger = get_logger("internal_client.seller")


class InternalSellerClient:
    """seller 도메인 internal API 호출 wrapper. stateless — Singleton OK."""

    def __init__(self, *, timeout_s: float = 5.0):
        self._client = httpx.AsyncClient(
            base_url=settings.BACKEND_SERVICE_URL,
            timeout=timeout_s,
            headers={"X-Internal-Token": settings.INTERNAL_SERVICE_TOKEN},
        )


    async def close(self) -> None:
        await self._client.aclose()


    async def find_product(self, product_id: str) -> Optional[ProductResponse]:
        """없으면 None."""
        try:
            resp = await self._client.get(
                f"/api/internal/seller/products/{product_id}",
            )
        except httpx.HTTPError as e:
            logger.warning("find_product 네트워크 오류 product_id={}: {}", product_id, e)
            raise BackendUnavailableError(f"backend 호출 실패: {e}") from e

        if resp.status_code == 404:
            return None
        if 500 <= resp.status_code < 600:
            raise BackendUnavailableError(
                f"backend 5xx (status={resp.status_code} product_id={product_id})",
            )
        if resp.status_code >= 400:
            raise BackendUnavailableError(
                f"backend {resp.status_code}: {resp.text[:200]}",
            )
        return ProductResponse.model_validate(resp.json())


    async def get_today_operation(self, store_id: str) -> Optional[TodayOperationResponse]:
        """오늘 영업 정보. None = 오늘 영업일 아님."""
        try:
            resp = await self._client.get(
                f"/api/internal/seller/stores/{store_id}/today-operation",
            )
        except httpx.HTTPError as e:
            logger.warning(
                "get_today_operation 네트워크 오류 store_id={}: {}", store_id, e,
            )
            raise BackendUnavailableError(f"backend 호출 실패: {e}") from e

        if resp.status_code == 404:
            return None
        if 500 <= resp.status_code < 600:
            raise BackendUnavailableError(
                f"backend 5xx (status={resp.status_code} store_id={store_id})",
            )
        if resp.status_code >= 400:
            raise BackendUnavailableError(
                f"backend {resp.status_code}: {resp.text[:200]}",
            )
        return TodayOperationResponse.model_validate(resp.json())


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
            raise BackendUnavailableError(f"backend 호출 실패: {e}") from e

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
                f"backend 5xx (status={resp.status_code})",
            )
        raise BackendUnavailableError(
            f"backend {resp.status_code}: {resp.text[:200]}",
        )


    async def restore_stock(
        self, *, payment_id: str, product_id: str, quantity: int,
    ) -> None:
        """payment_id 단위 멱등 (서버 측 ledger 가 보장). retry / sweep 중복 트리거 안전.

        실패는 무조건 raise (caller 가 critical 로깅 결정).

        Raises:
            StockInsufficientError: 누계 차감보다 많이 복원 요청 (400) — caller 버그 신호.
            StockConflictError:     낙관적 락 충돌 (409).
            BackendUnavailableError: 5xx / 네트워크 / 그 외.
        """
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
            raise BackendUnavailableError(f"backend 호출 실패: {e}") from e

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
                f"backend 5xx (status={resp.status_code})",
            )
        raise BackendUnavailableError(
            f"backend {resp.status_code}: {resp.text[:200]}",
        )


    async def get_store_id_by_seller_email(self, seller_email: str) -> str:
        """seller_email → store_id.

        Raises:
            StoreNotFoundError:      backend 가 404 — 가게가 없음. DomainError 로 bubble.
            BackendUnavailableError: 5xx / 네트워크 / 그 외 4xx.
        """
        try:
            resp = await self._client.get(
                "/api/internal/seller/store-id",
                params={"seller_email": seller_email},
            )
        except httpx.HTTPError as e:
            raise BackendUnavailableError(f"backend 호출 실패: {e}") from e

        if resp.status_code == 200:
            return resp.json()["store_id"]
        if resp.status_code == 404:
            raise StoreNotFoundError("가게를 찾을 수 없습니다")
        raise BackendUnavailableError(
            f"backend {resp.status_code}: {resp.text[:200]}",
        )


def _extract_detail(resp: httpx.Response) -> Optional[str]:
    try:
        return resp.json().get("detail")
    except (ValueError, AttributeError):
        return None
