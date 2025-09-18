from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


from schemas.order import OrderStatus


class CustomerOrderItemResponse(BaseModel):
    payment_id: str = Field(..., description="결제 고유 ID")
    product_id: str = Field(..., description="상품 고유 ID")
    product_name: str = Field(..., description="상품 이름")
    store_id: str = Field(..., description="가게 고유 ID")
    store_name: str = Field(..., description="가게 이름")
    quantity: int = Field(..., description="구매 수량")
    price: int = Field(..., description="최종 가격 (원)")
    status: OrderStatus = Field(..., description="주문 상태")
    reservation_at: datetime = Field(..., description="예약 주문 시간")
    accepted_at: Optional[datetime] = Field(None, description="주문 수락 시간")
    completed_at: Optional[datetime] = Field(None, description="픽업 완료 시간")
    canceled_at: Optional[datetime] = Field(None, description="주문 취소 시간")
    
    class Config:
        from_attributes = True


class CustomerOrderListResponse(BaseModel):
    orders: List[CustomerOrderItemResponse] = Field(default_factory=list, description="주문 목록")
    total: int = Field(..., description="전체 주문 수")


class CustomerOrderDetailResponse(BaseModel):
    payment_id: str = Field(..., description="결제 고유 ID")
    product_id: str = Field(..., description="상품 고유 ID")
    product_name: str = Field(..., description="상품 이름")
    store_id: str = Field(..., description="가게 고유 ID")
    store_name: str = Field(..., description="가게 이름")
    quantity: int = Field(..., description="구매 수량")
    price: int = Field(..., description="최종 가격 (원)")
    unit_price: int = Field(..., description="단가 (원)")
    discount_rate: Optional[int] = Field(None, description="할인율")
    status: OrderStatus = Field(..., description="주문 상태")
    reservation_at: datetime = Field(..., description="예약 주문 시간")
    accepted_at: Optional[datetime] = Field(None, description="주문 수락 시간")
    completed_at: Optional[datetime] = Field(None, description="픽업 완료 시간")
    canceled_at: Optional[datetime] = Field(None, description="주문 취소 시간")
    
    class Config:
        from_attributes = True

class CustomerOrderCancelRequest(BaseModel):
    reason: str = Field(default="개인 사정", description="환불 사유")


class CustomerOrderCancelResponse(BaseModel):
    payment_id: str = Field(..., description="결제 고유 ID")
    refunded_amount: int = Field(..., description="환불 금액")
    

class PickupCompleteRequest(BaseModel):
    qr_data: str = Field(..., description="QR 코드 데이터")