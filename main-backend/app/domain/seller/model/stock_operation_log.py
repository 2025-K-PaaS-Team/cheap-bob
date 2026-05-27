"""(payment_id, op_type) 단위 stock 조작 멱등성 로그.

payment-backend 가 main-backend 의 /api/internal/seller/products/.../{consume,restore}-stock
를 retry 호출해도 같은 (payment_id, op_type) 조합은 한 번만 적용되도록 PK + INSERT ON
CONFLICT DO NOTHING 으로 보장한다.

product_id / quantity 는 추적용 (디버깅/감사). 실제 dedupe 는 PK 만으로 충분.
"""
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import DateTime, Integer, String, func
from datetime import datetime

from app.database.session import Base


class StockOperationLog(Base):
    __tablename__ = "stock_operation_log"

    payment_id: Mapped[str] = mapped_column(String(255), primary_key=True)
    op_type: Mapped[str] = mapped_column(String(16), primary_key=True)
    product_id: Mapped[str] = mapped_column(String(255), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    applied_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False,
    )
