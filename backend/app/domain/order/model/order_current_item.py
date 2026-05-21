from typing import TYPE_CHECKING, Optional
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String
from datetime import datetime

from app.domain.order.dto.order import OrderStatus
from app.database.session import Base


if TYPE_CHECKING:
    from app.domain.seller.model.store_product_info import StoreProductInfo
    from app.domain.auth.model.customer import Customer


class OrderCurrentItem(Base):
    """주문 내역 — 당일 보관 (다음날 새벽 batch 가 OrderHistoryItem 으로 이관)."""

    __tablename__ = "order_current_items"
    __mapper_args__ = {"eager_defaults": True}

    payment_id: Mapped[str] = mapped_column(String(255), primary_key=True)
    product_id: Mapped[str] = mapped_column(
        String(255), ForeignKey("store_product_info.product_id"),
    )
    customer_id: Mapped[str] = mapped_column(
        String(255), ForeignKey("customers.email"),
    )
    quantity: Mapped[int] = mapped_column(Integer)
    price: Mapped[int] = mapped_column(Integer)
    sale: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    total_amount: Mapped[int] = mapped_column(Integer)
    status: Mapped[OrderStatus] = mapped_column(
        Enum(OrderStatus), default=OrderStatus.reservation,
    )
    reservation_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(),
    )
    accepted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True,
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True,
    )
    canceled_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True,
    )
    cancel_reason: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # 주문 시점에 캡처된 소비자 선호 (콤마 구분). 추후 history 로 함께 이관.
    preferred_menus: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    nutrition_types: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    allergies: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    topping_types: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    product: Mapped["StoreProductInfo"] = relationship(
        "StoreProductInfo", back_populates="order_current_items",
    )
    customer: Mapped["Customer"] = relationship(
        "Customer", foreign_keys=[customer_id],
    )
