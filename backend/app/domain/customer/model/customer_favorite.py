from typing import TYPE_CHECKING
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import DateTime, ForeignKey, String
from datetime import datetime

from app.database.session import Base


if TYPE_CHECKING:
    from app.domain.seller.model.store import Store
    from app.domain.auth.model.customer import Customer


class CustomerFavorite(Base):
    """소비자 즐겨찾기 가게."""

    __tablename__ = "customer_favorites"
    __mapper_args__ = {"eager_defaults": True}

    customer_email: Mapped[str] = mapped_column(
        String(255), ForeignKey("customers.email"), primary_key=True,
    )
    store_id: Mapped[str] = mapped_column(
        String(255), ForeignKey("stores.store_id"), primary_key=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(),
    )

    customer: Mapped["Customer"] = relationship("Customer", back_populates="favorites")
    # store 도메인이 분리되지 않은 동안은 legacy 위치의 Store 와 연결된다.
    store: Mapped["Store"] = relationship("Store", back_populates="favorited_by")
