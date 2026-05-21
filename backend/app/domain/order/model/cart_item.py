from typing import TYPE_CHECKING, Optional
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import DateTime, ForeignKey, Integer, String
from datetime import datetime

from app.database.session import Base


if TYPE_CHECKING:
    from app.domain.seller.model.store_product_info import StoreProductInfo


class CartItem(Base):
    """장바구니 — 결제 진행중 임시 재고 차감 기록."""

    __tablename__ = "cart_items"
    __mapper_args__ = {"eager_defaults": True}

    payment_id: Mapped[str] = mapped_column(String(255), primary_key=True)
    product_id: Mapped[str] = mapped_column(
        String(255), ForeignKey("store_product_info.product_id"),
    )
    customer_id: Mapped[str] = mapped_column(String(255))
    quantity: Mapped[int] = mapped_column(Integer)
    price: Mapped[int] = mapped_column(Integer)
    sale: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    total_amount: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(),
    )

    product: Mapped["StoreProductInfo"] = relationship(
        "StoreProductInfo", back_populates="cart_items",
    )
