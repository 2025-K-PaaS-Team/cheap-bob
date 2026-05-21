from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

from app.domain.order.dto.order import OrderStatus


class OrderItemResponse(BaseModel):
    payment_id: str = Field(..., description="결제 고유 ID")
    customer_id: str = Field(..., description="소비자 고유 ID")
    customer_nickname: str = Field(..., description="소비자 이름")
    customer_phone_number: str = Field(..., description="소비자 핸드폰 번호")
    product_id: str = Field(..., description="상품 고유 ID")
    product_name: str = Field(..., description="상품 이름")
    store_id: str = Field(..., description="가게 고유 ID")
    store_name: str = Field(..., description="가게 이름")
    quantity: int = Field(..., description="구매 수량")
    price: int = Field(..., description="원가 (원)")
    sale: Optional[int] = Field(None, description="세일 퍼센트")
    total_amount: int = Field(..., description="총 결제 금액")
    status: OrderStatus = Field(..., description="주문 상태")
    reservation_at: datetime = Field(..., description="예약 주문 시간")
    accepted_at: Optional[datetime] = Field(None, description="주문 수락 시간")
    completed_at: Optional[datetime] = Field(None, description="픽업 완료 시간")
    canceled_at: Optional[datetime] = Field(None, description="주문 취소 시간")
    cancel_reason: Optional[str] = Field(None, description="취소 사유")
    preferred_menus: Optional[List[str]] = Field(None)
    nutrition_types: Optional[List[str]] = Field(None)
    allergies: Optional[List[str]] = Field(None)
    topping_types: Optional[List[str]] = Field(None)


    class Config:
        from_attributes = True


class OrderListResponse(BaseModel):
    orders: List[OrderItemResponse] = Field(default_factory=list)
    total: int = Field(...)


class CustomerOrderItemResponse(OrderItemResponse):
    main_image_url: Optional[str] = Field(None, description="대표 이미지 URL")


class CustomerOrderListResponse(BaseModel):
    orders: List[CustomerOrderItemResponse] = Field(default_factory=list)
    total: int = Field(...)


class CustomerTodayOrderItemResponse(CustomerOrderItemResponse):
    pickup_start_time: str = Field(..., description="가게 픽업 시작 시간 (HH:MM)")
    pickup_end_time: str = Field(..., description="픽업 종료 시간 (HH:MM)")


class CustomerTodayOrderListResponse(BaseModel):
    orders: List[CustomerTodayOrderItemResponse] = Field(default_factory=list)
    total: int = Field(...)


class OrderCancelRequest(BaseModel):
    reason: str = Field(
        default="‘요청’ 으로 주문이 취소되었어요.",
        description="환불 사유",
        min_length=1, max_length=255,
    )


class OrderCancelResponse(BaseModel):
    payment_id: str = Field(..., description="결제 고유 ID")
    quantity: int = Field(..., description="구매 수량")
    price: int = Field(..., description="원가 (원)")
    sale: Optional[int] = Field(None, description="세일 퍼센트")
    total_amount: int = Field(..., description="총 결제 금액")


class CustomerPickupCompleteRequest(BaseModel):
    qr_data: str = Field(..., description="QR 코드 데이터")


class SellerPickupQRResponse(BaseModel):
    payment_id: str = Field(..., description="결제 고유 ID")
    qr_data: str = Field(..., description="QR 코드 데이터")
    created_at: datetime = Field(..., description="QR 생성 시간")


class TodayAlarmOrderCard(BaseModel):
    """오늘의 알림용 주문 카드."""
    payment_id: str = Field(...)
    order_time: datetime = Field(..., description="주문 상태별 시간")
    quantity: int
    price: int
    sale: Optional[int] = Field(None)
    total_amount: int
    status: OrderStatus
    store_name: str
    product_name: str
    pickup_start_time: str = Field(..., description="HH:MM")
    pickup_end_time: str = Field(..., description="HH:MM")


    class Config:
        from_attributes = True


class TodayAlarmResponse(BaseModel):
    alarm_cards: List[TodayAlarmOrderCard] = Field(default_factory=list)
    total: int
