from typing import TYPE_CHECKING
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String
from datetime import datetime

from app.domain.customer.dto.preference import AllergyType
from app.database.session import Base


if TYPE_CHECKING:
    from app.domain.customer.model.customer import Customer


class CustomerAllergy(Base):
    """소비자 알레르기 / 제약 조건."""

    __tablename__ = "customer_allergies"
    __mapper_args__ = {"eager_defaults": True}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    customer_email: Mapped[str] = mapped_column(
        String(255), ForeignKey("customers.email"),
    )
    allergy_type: Mapped[AllergyType] = mapped_column(Enum(AllergyType))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(),
    )

    customer: Mapped["Customer"] = relationship(
        "Customer", back_populates="allergies",
    )
