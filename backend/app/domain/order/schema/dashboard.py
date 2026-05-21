from typing import List
from pydantic import BaseModel, Field


class DashboardStockItem(BaseModel):
    product_id: str = Field(..., description="상품 고유 ID")
    product_name: str = Field(..., description="상품 이름")
    current_stock: int = Field(..., description="현재 남아있는 재고")
    initial_stock: int = Field(..., description="최초 설정 재고")
    purchased_stock: int = Field(..., description="구매된 수량 (cancel 제외)")
    adjustment_stock: int = Field(..., description="판매자 조절 누계")


    class Config:
        from_attributes = True


class DashboardResponse(BaseModel):
    items: List[DashboardStockItem] = Field(default_factory=list)
    total_items: int = Field(...)
