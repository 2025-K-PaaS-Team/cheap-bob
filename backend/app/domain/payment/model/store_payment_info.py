from typing import TYPE_CHECKING, Optional
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, String

from app.database.session import Base


if TYPE_CHECKING:
    from app.domain.seller.model.store import Store


class StorePaymentInfo(Base):
    """가게 결제 정보 (포트원 연동 자격증명)."""

    __tablename__ = "store_payment_info"
    __mapper_args__ = {"eager_defaults": True}

    store_id: Mapped[str] = mapped_column(
        String(255), ForeignKey("stores.store_id"), primary_key=True,
    )
    portone_store_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    portone_channel_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    portone_secret_key: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    store: Mapped["Store"] = relationship("Store", back_populates="payment_info")
