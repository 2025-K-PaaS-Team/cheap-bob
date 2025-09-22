import enum
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

class OrderStatus(enum.Enum):
    reservation = "reservation" # 예약 중
    accept = "accept" # 주문 수락
    complete = "complete" # 픽업 완료
    cancel = "cancel" # 취소
    
class OrderItemResponse(BaseModel):
    payment_id: str = Field(..., description="결제 고유 ID")
    product_id: str = Field(..., description="상품 고유 ID")
    product_name: str = Field(..., description="상품 이름")
    store_id: str = Field(..., description="가게 고유 ID")
    store_name: str = Field(..., description="가게 이름")
    quantity: int = Field(..., description="구매 수량")
    price: int = Field(..., description="원가 (원)")
    sale: Optional[int] = Field(None, description="세일 퍼센트")
    status: OrderStatus = Field(..., description="주문 상태")
    reservation_at: datetime = Field(..., description="예약 주문 시간")
    accepted_at: Optional[datetime] = Field(None, description="주문 수락 시간")
    completed_at: Optional[datetime] = Field(None, description="픽업 완료 시간")
    canceled_at: Optional[datetime] = Field(None, description="주문 취소 시간")
    cancel_reason: Optional[str] = Field(None, description="취소 사유")
    preferred_menus: Optional[List[str]] = Field(default=None, description="유저의 선호 메뉴")
    nutrition_types: Optional[List[str]] = Field(default=None, description="식품 영양 타입")
    allergies: Optional[List[str]] = Field(default=None, description="알레르기/제약조건")
    topping_types: Optional[List[str]] = Field(default=None, description="선호 토핑")
    
    class Config:
        from_attributes = True
        
class OrderListResponse(BaseModel):
    orders: List[OrderItemResponse] = Field(default_factory=list, description="주문 목록")
    total: int = Field(..., description="전체 주문 수")

class OrderCancelRequest(BaseModel):
    reason: str = Field(default="개인 사정", description="환불 사유", min_length=1, max_length=255)


class OrderCancelResponse(BaseModel):
    payment_id: str = Field(..., description="결제 고유 ID")
    refunded_amount: int = Field(..., description="환불 금액")
    

class CustomerPickupCompleteRequest(BaseModel):
    qr_data: str = Field(..., description="QR 코드 데이터")


class SellerPickupQRResponse(BaseModel):
    payment_id: str = Field(..., description="결제 고유 ID")
    qr_data: str = Field(..., description="QR 코드 데이터")
    created_at: datetime = Field(..., description="QR 생성 시간")
