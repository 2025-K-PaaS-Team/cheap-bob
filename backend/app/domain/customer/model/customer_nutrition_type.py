from typing import TYPE_CHECKING
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String
from datetime import datetime

from app.domain.seller.dto.nutrition import NutritionType
from app.database.session import Base


if TYPE_CHECKING:
    from app.domain.customer.model.customer import Customer


class CustomerNutritionType(Base):
    """소비자 영양 타입."""

    __tablename__ = "customer_nutrition_types"
    __mapper_args__ = {"eager_defaults": True}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    customer_email: Mapped[str] = mapped_column(
        String(255), ForeignKey("customers.email"),
    )
    nutrition_type: Mapped[NutritionType] = mapped_column(Enum(NutritionType))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(),
    )

    customer: Mapped["Customer"] = relationship(
        "Customer", back_populates="nutrition_types",
    )
