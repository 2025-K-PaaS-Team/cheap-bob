"""payment-backend <-> main-backend 간 internal API 의 request/response 모델.

shared 패턴 미적용 — main-backend 측에도 동일한 schema 가 자체 정의로 존재한다.
계약이 바뀔 때는 양쪽을 같이 수정.
"""
from typing import Optional
from pydantic import BaseModel, Field


# ───────── payment-backend → main-backend 호출 ─────────


class ProductResponse(BaseModel):
    """GET /internal/seller/products/{product_id}"""
    product_id: str
    store_id: str
    product_name: str
    price: int
    sale: Optional[int] = None
    current_stock: int


class TodayOperationResponse(BaseModel):
    """GET /internal/seller/stores/{store_id}/today-operation

    None 응답은 200 with `null` 이 아니라 404 로 처리.
    """
    operation_id: int
    day_of_week: int
    is_open_enabled: bool
    is_currently_open: bool
    pickup_start_time: str  # ISO time HH:MM:SS
    pickup_end_time: str


class ConsumeStockRequest(BaseModel):
    payment_id: str  # 멱등 키
    product_id: str
    quantity: int


class RestoreStockRequest(BaseModel):
    payment_id: str  # 멱등 키
    product_id: str
    quantity: int


class CreateOrderFromCartRequest(BaseModel):
    """payment-backend → main-backend: 결제 finalize 시 order_current_item 생성.

    payment_id 가 UNIQUE 멱등 키 — 같은 payment_id 로 두 번 호출되면 두 번째는 no-op.
    customer preference snapshot 은 main-backend 가 내부적으로 lookup.
    """
    payment_id: str
    product_id: str
    customer_id: str
    quantity: int
    price: int
    sale: Optional[int] = None
    total_amount: int


# ───────── main-backend → payment-backend 호출 ─────────


class StorePaymentInfoInternalResponse(BaseModel):
    """GET /internal/payment/store-info/{store_id}"""
    store_id: str
    portone_store_id: Optional[str] = None
    portone_channel_id: Optional[str] = None
    portone_secret_key: Optional[str] = None


class StorePaymentRegisterRequest(BaseModel):
    """POST /internal/payment/store-info — 가게 1차 등록."""
    store_id: str
    portone_store_id: str
    portone_channel_id: str
    portone_secret_key: str = Field(..., min_length=1)


class RefundRequest(BaseModel):
    """POST /internal/payment/refund — 환불 트리거 (order cancel / store close)."""
    payment_id: str
    store_id: str  # main-backend 에 secret_key 가 없으니 store_id 로 payment-backend 내부 조회
    reason: str


class HasCompleteInfoResponse(BaseModel):
    """GET /internal/payment/store-info/{store_id}/has-complete"""
    has_complete: bool


class ExistsInfoResponse(BaseModel):
    """GET /internal/payment/store-info/{store_id}/exists — 완전성 무관, row 존재 여부만."""
    exists: bool
