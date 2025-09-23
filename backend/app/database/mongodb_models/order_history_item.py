from datetime import datetime, timezone
from typing import Optional
from pydantic import Field

from database.mongodb_models.base import Document


class OrderHistoryItem(Document):
    """오래된 주문 히스토리"""
    
    payment_id: str = Field(..., description="구매 고유 ID")
    product_id: str = Field(..., description="상품 고유 ID")
    user_id: str = Field(..., description="유저 고유 ID")
    quantity: int = Field(..., description="구매 수량")
    price: int = Field(..., description="원가 (원)")
    sale: Optional[int] = Field(None, description="세일 퍼센트")
    total_amount: int = Field(..., description="최종 금액")
    status: str = Field(default="reservation", description="상태")
    reservation_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), 
        description="예약 주문 시간"
    )
    accepted_at: Optional[datetime] = Field(None, description="주문 수락 시간")
    completed_at: Optional[datetime] = Field(None, description="픽업 완료 시간")
    canceled_at: Optional[datetime] = Field(None, description="주문 취소 시간")
    cancel_reason: Optional[str] = Field(None, max_length=500, description="취소 사유")
    
    preferred_menus: Optional[str] = Field(None, max_length=500, description="유저의 선호 메뉴 (콤마로 구분)")
    nutrition_types: Optional[str] = Field(None, max_length=500, description="식품 영양 타입 (콤마로 구분)")
    allergies: Optional[str] = Field(None, max_length=500, description="알레르기/제약조건 (콤마로 구분)")
    topping_types: Optional[str] = Field(None, max_length=500, description="선호 토핑 (콤마로 구분)")
    
    class Settings:
        name = "order_history_items"
        indexes = [
            [("user_id", 1)],
            [("product_id", 1)],
            [("reservation_at", -1)],
        ]