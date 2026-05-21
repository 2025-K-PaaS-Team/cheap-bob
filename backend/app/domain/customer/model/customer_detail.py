from typing import TYPE_CHECKING
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import DateTime, ForeignKey, String
from datetime import datetime

from app.database.session import Base


if TYPE_CHECKING:
    from app.domain.auth.model.customer import Customer


class CustomerDetail(Base):
    """소비자 상세 정보."""

    __tablename__ = "customer_details"
    __mapper_args__ = {"eager_defaults": True}

    customer_email: Mapped[str] = mapped_column(
        String(255), ForeignKey("customers.email"), primary_key=True,
    )
    nickname: Mapped[str] = mapped_column(String(7))           # 1-7자, 중복 허용
    phone_number: Mapped[str] = mapped_column(String(11))      # 11자리 숫자
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(),
    )

    customer: Mapped["Customer"] = relationship("Customer", back_populates="detail")
