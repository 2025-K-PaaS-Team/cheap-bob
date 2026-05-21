from typing import List
from pydantic import BaseModel, Field

from app.domain.order.dto.order import OrderStatus


class SettlementItem(BaseModel):
    product_name: str = Field(..., description="상품 이름")
    quantity: int = Field(..., description="판매된 개수")
    total_amount: int = Field(..., description="최종 판매가")
    status: OrderStatus = Field(..., description="complete / cancel")
    time_at: str = Field(..., description="시간 (HH:MM)")


class SettlementDayGroup(BaseModel):
    date: str = Field(..., description="날짜 KST (YYYY-MM-DD)")
    items: List[SettlementItem] = Field(default_factory=list)


class SettlementResponse(BaseModel):
    daily_settlements: List[SettlementDayGroup] = Field(default_factory=list)


class WeeklyRevenueResponse(BaseModel):
    total_revenue: int = Field(..., description="이번 주 월요일~오늘 complete 주문 총 매출")
