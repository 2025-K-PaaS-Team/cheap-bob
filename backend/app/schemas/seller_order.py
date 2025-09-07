from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
import enum

class OrderStatus(enum.Enum):
    reservation = "reservation" # 예약 중
    accepted = "accepted" # 주문 수락
    pickup = "pickup" # 픽업 준비 완료
    complete = "complete" # 픽업 완료
    cancel = "cancel" # 취소

class OrderItemResponse(BaseModel):
    payment_id: str = Field(..., description="결제 고유 ID")
    product_id: str = Field(..., description="상품 고유 ID")
    product_name: str = Field(..., description="상품 이름")
    quantity: int = Field(..., description="구매 수량")
    price: int = Field(..., description="최종 가격 (원)")
    status: OrderStatus = Field(..., description="주문 상태")
    reservation_at: datetime = Field(..., description="예약 주문 시간")
    accepted_at: Optional[datetime] = Field(None, description="주문 수락 시간")
    pickup_ready_at: Optional[datetime] = Field(None, description="픽업 준비 완료 시간")
    completed_at: Optional[datetime] = Field(None, description="픽업 완료 시간")
    
    class Config:
        from_attributes = True


class OrderListResponse(BaseModel):
    orders: List[OrderItemResponse] = Field(default_factory=list, description="주문 목록")
    total: int = Field(..., description="전체 주문 수")


class OrderCancelRequest(BaseModel):
    reason: str = Field("판매자 요청", description="취소 사유", min_length=1, max_length=255)


class OrderCancelResponse(BaseModel):
    payment_id: str = Field(..., description="결제 고유 ID")
    status: str = Field(..., description="취소 상태")
    message: str = Field(..., description="취소 메시지")
    refunded_amount: int = Field(..., description="환불 금액")


class PickupQRResponse(BaseModel):
    payment_id: str = Field(..., description="결제 고유 ID")
    qr_data: str = Field(..., description="QR 코드 데이터")
    created_at: datetime = Field(..., description="QR 생성 시간")


class PickupCompleteRequest(BaseModel):
    qr_data: str = Field(..., description="QR 코드 데이터")