from typing import Optional
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String

from app.database.session import Base


class StorePaymentInfo(Base):
    """가게 결제 정보 (포트원 연동 자격증명).

    payment-svc 가 소유. store_id 는 backend 의 stores.store_id 와 논리적으로 매칭하나
    FK 는 없다 (다른 DB) — 단순 string 값.
    """

    __tablename__ = "store_payment_info"
    __mapper_args__ = {"eager_defaults": True}

    store_id: Mapped[str] = mapped_column(String(255), primary_key=True)
    portone_store_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    portone_channel_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    portone_secret_key: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
