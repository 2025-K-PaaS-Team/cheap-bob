"""seller 도메인의 internal API — payment-svc 가 호출.

shared 패턴 미적용 — payment-svc 의 dto/internal.py 와 일치하는 schema 를 본 모듈에 자체
정의한다. 계약 변경 시 양쪽을 같이 수정.

consume/restore 는 (payment_id, op_type) 기준 **진짜 멱등** — StockIdempotencyService 의
stock_operation_log INSERT ON CONFLICT DO NOTHING 으로 retry / 중복 호출 안전.
"""
from typing import Optional
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, status
from dependency_injector.wiring import Provide, inject

from app.middleware.internal_token import require_internal_token
from app.domain.seller.service.stock_idempotency import StockIdempotencyService
from app.domain.seller.service.seller_store_read import SellerStoreReadService
from app.domain.seller.service.seller_product import SellerProductService
from app.domain.seller.service.exception import (
    ProductStockConflictError,
    ProductStockInsufficientError,
    StoreNotFoundError,
)


# ───────── schemas (payment-svc 의 dto/internal.py 와 1:1 매칭) ─────────


class ProductResponse(BaseModel):
    product_id: str
    store_id: str
    product_name: str
    price: int
    sale: Optional[int] = None
    current_stock: int


class TodayOperationResponse(BaseModel):
    operation_id: int
    day_of_week: int
    is_open_enabled: bool
    is_currently_open: bool
    pickup_start_time: str
    pickup_end_time: str


class StockOpRequest(BaseModel):
    payment_id: str  # (payment_id, op_type) 멱등 키. stock_operation_log PK.
    product_id: str
    quantity: int


class StoreIdResponse(BaseModel):
    store_id: str


# ───────── router ─────────


internal_router = APIRouter(
    # 최종 등록 경로 = /api/internal (집계기) + /seller = /api/internal/seller/...
    prefix="/seller",
    tags=["Internal/Seller"],
    dependencies=[Depends(require_internal_token)],
)


@internal_router.get(
    "/products/{product_id}",
    response_model=ProductResponse,
)
@inject
async def get_product(
    product_id: str,
    seller_product_service: SellerProductService = Depends(
        Provide["seller_product_service"],
    ),
):
    product = await seller_product_service.find_product(product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="상품을 찾을 수 없습니다")
    return ProductResponse(
        product_id=product.product_id,
        store_id=product.store_id,
        product_name=product.product_name,
        price=product.price,
        sale=product.sale,
        current_stock=product.current_stock,
    )


@internal_router.get(
    "/stores/{store_id}/today-operation",
    response_model=TodayOperationResponse,
)
@inject
async def get_today_operation(
    store_id: str,
    seller_store_read_service: SellerStoreReadService = Depends(
        Provide["seller_store_read_service"],
    ),
):
    """오늘 영업일 정보. 영업일 아니거나 가게 없으면 404."""
    op = await seller_store_read_service.get_today_operation(store_id)
    if op is None:
        raise HTTPException(status_code=404, detail="오늘은 영업일이 아닙니다")
    return TodayOperationResponse(
        operation_id=op.operation_id,
        day_of_week=op.day_of_week,
        is_open_enabled=op.is_open_enabled,
        is_currently_open=op.is_currently_open,
        pickup_start_time=op.pickup_start_time.strftime("%H:%M:%S"),
        pickup_end_time=op.pickup_end_time.strftime("%H:%M:%S"),
    )


@internal_router.post(
    "/products/{product_id}/consume-stock",
    status_code=status.HTTP_204_NO_CONTENT,
)
@inject
async def consume_stock(
    product_id: str,
    request: StockOpRequest,
    stock_idempotency_service: StockIdempotencyService = Depends(
        Provide["stock_idempotency_service"],
    ),
):
    """payment-svc 의 결제 init 시 호출. 재고 부족 → 400, 낙관적 락 충돌 → 409.

    (payment_id, "consume") PK 로 멱등 — 같은 키의 재호출은 204 with no-op.
    """
    if request.product_id != product_id:
        raise HTTPException(status_code=400, detail="product_id 불일치")
    try:
        await stock_idempotency_service.consume(
            payment_id=request.payment_id,
            product_id=product_id,
            quantity=request.quantity,
        )
    except ProductStockInsufficientError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ProductStockConflictError as e:
        raise HTTPException(status_code=409, detail=str(e))


@internal_router.post(
    "/products/{product_id}/restore-stock",
    status_code=status.HTTP_204_NO_CONTENT,
)
@inject
async def restore_stock(
    product_id: str,
    request: StockOpRequest,
    stock_idempotency_service: StockIdempotencyService = Depends(
        Provide["stock_idempotency_service"],
    ),
):
    """payment-svc 의 보상/취소 시 호출. (payment_id, "restore") PK 로 멱등."""
    if request.product_id != product_id:
        raise HTTPException(status_code=400, detail="product_id 불일치")
    await stock_idempotency_service.restore(
        payment_id=request.payment_id,
        product_id=product_id,
        quantity=request.quantity,
    )


@internal_router.get(
    "/store-id",
    response_model=StoreIdResponse,
)
@inject
async def get_store_id_by_seller_email(
    seller_email: str,
    seller_store_read_service: SellerStoreReadService = Depends(
        Provide["seller_store_read_service"],
    ),
):
    """seller_email → store_id. payment-svc 의 seller_settings 라우터가 호출."""
    try:
        store_id = await seller_store_read_service.get_store_id_by_seller_email(
            seller_email,
        )
    except StoreNotFoundError:
        raise HTTPException(status_code=404, detail="가게를 찾을 수 없습니다")
    return StoreIdResponse(store_id=store_id)
