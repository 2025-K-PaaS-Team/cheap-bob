from typing import TYPE_CHECKING
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from datetime import datetime

from app.database.session import Base


if TYPE_CHECKING:
    from app.domain.seller.model.store import Store


class StoreImage(Base):
    """가게 이미지 (대표/추가 이미지)."""

    __tablename__ = "store_images"
    __mapper_args__ = {"eager_defaults": True}

    image_id: Mapped[str] = mapped_column(String(255), primary_key=True)
    store_id: Mapped[str] = mapped_column(
        String(255), ForeignKey("stores.store_id"),
    )
    is_main: Mapped[bool] = mapped_column(Boolean, default=False)
    display_order: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(),
    )

    store: Mapped["Store"] = relationship("Store", back_populates="images")
