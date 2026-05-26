from typing import TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Enum, ForeignKey, String

from app.domain.seller.dto.nutrition import NutritionType
from app.database.session import Base


if TYPE_CHECKING:
    from app.domain.seller.model.store_product_info import StoreProductInfo


class ProductNutrition(Base):
    """상품 영양 정보 (상품 ↔ NutritionType N:M 매핑)."""

    __tablename__ = "product_nutrition"

    product_id: Mapped[str] = mapped_column(
        String(255), ForeignKey("store_product_info.product_id"), primary_key=True,
    )
    nutrition_type: Mapped[NutritionType] = mapped_column(
        Enum(NutritionType), primary_key=True,
    )

    product: Mapped["StoreProductInfo"] = relationship(
        "StoreProductInfo", back_populates="nutrition_info",
    )
