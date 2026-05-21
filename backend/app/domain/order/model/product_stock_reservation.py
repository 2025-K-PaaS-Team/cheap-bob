from pydantic import Field
from datetime import datetime, timezone
from pymongo import ASCENDING, IndexModel

from app.database.mongodb_document import Document


class ProductStockReservation(Document):
    """상품 재고 변경 예약 — 가게가 미리 잡아두는 다음날 적용 예약."""

    product_id: str = Field(..., description="상품 ID")
    initial_stock: int = Field(..., description="예약 시점의 재고량")
    new_stock: int = Field(..., description="변경 예정 재고량")
    reserved_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="예약 생성 시간",
    )


    class Settings:
        name = "product_stock_reservations"
        indexes = [
            IndexModel([("product_id", ASCENDING)], unique=True),
        ]
        use_state_management = True
