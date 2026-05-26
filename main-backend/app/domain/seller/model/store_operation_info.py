from typing import TYPE_CHECKING, Optional
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, Integer, String, Time
from datetime import datetime, time

from app.database.session import Base


if TYPE_CHECKING:
    from app.domain.seller.model.store_operation_info_modification import (
        StoreOperationInfoModification,
    )
    from app.domain.seller.model.store import Store


class StoreOperationInfo(Base):
    """가게 운영 정보 (요일별)."""

    __tablename__ = "store_operation_info"

    operation_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    store_id: Mapped[str] = mapped_column(
        String(255), ForeignKey("stores.store_id"),
    )
    day_of_week: Mapped[int] = mapped_column(Integer)  # 0: 월요일 ~ 6: 일요일

    open_time: Mapped[time] = mapped_column(Time)
    pickup_start_time: Mapped[time] = mapped_column(Time)
    pickup_end_time: Mapped[time] = mapped_column(Time)
    close_time: Mapped[time] = mapped_column(Time)

    is_open_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    is_currently_open: Mapped[bool] = mapped_column(Boolean, default=False)

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(),
    )

    store: Mapped["Store"] = relationship("Store", back_populates="operation_info")
    modification: Mapped[Optional["StoreOperationInfoModification"]] = relationship(
        "StoreOperationInfoModification",
        back_populates="operation_info",
        uselist=False,
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        CheckConstraint("day_of_week >= 0 AND day_of_week <= 6"),
        CheckConstraint("open_time < close_time"),
        CheckConstraint(
            "pickup_start_time >= open_time AND pickup_start_time < close_time",
        ),
        CheckConstraint(
            "pickup_end_time > pickup_start_time AND pickup_end_time <= close_time",
        ),
        {"comment": "가게 운영 정보 (요일별)"},
    )
