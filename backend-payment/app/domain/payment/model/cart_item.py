from typing import Optional
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import DateTime, Integer, String
from datetime import datetime

from app.database.session import Base


class CartItem(Base):
    """장바구니 — 결제 진행중 임시 재고 차감 기록.

    payment-svc 가 소유. product_id 는 backend 의 store_product_info.product_id 와
    논리적으로 매칭하나 FK 는 없다 (다른 DB) — 단순 string 값.
    """

    __tablename__ = "cart_items"
    __mapper_args__ = {"eager_defaults": True}

    payment_id: Mapped[str] = mapped_column(String(255), primary_key=True)
    product_id: Mapped[str] = mapped_column(String(255), index=True)
    customer_id: Mapped[str] = mapped_column(String(255))
    quantity: Mapped[int] = mapped_column(Integer)
    price: Mapped[int] = mapped_column(Integer)
    sale: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    total_amount: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(),
    )
    # 결제 5분 timeout — sweeper worker 가 expires_at <= now() 를 만료로 처리.
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
