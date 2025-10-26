from datetime import datetime, timezone
from pydantic import Field
from database.mongodb_models.base import Document


class ProductStockReservation(Document):
    """상품 재고 변경 예약"""
    
    product_id: str = Field(..., description="상품 ID")
    initial_stock: int = Field(..., description="초기 재고 (예약 시점의 재고량)")
    new_stock: int = Field(..., description="변경 예정 재고량")
    reserved_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), 
        description="예약 시간"
    )
    
    class Settings:
        name = "product_stock_reservations"
        indexes = [
            [("product_id", 1), {"unique": True}]
        ]
        use_state_management = True