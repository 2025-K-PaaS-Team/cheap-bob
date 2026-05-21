from typing import TYPE_CHECKING, Optional
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, Integer, Time
from datetime import datetime, time

from app.database.session import Base


if TYPE_CHECKING:
    from app.domain.seller.model.store_operation_info import StoreOperationInfo


class StoreOperationInfoModification(Base):
    """가게 운영 정보 변경 예약 (다음 날 적용)."""

    __tablename__ = "store_operation_info_modifications"

    modification_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True,
    )
    operation_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("store_operation_info.operation_id"),
        unique=True,
    )

    new_open_time: Mapped[Optional[time]] = mapped_column(Time, nullable=True)
    new_pickup_start_time: Mapped[Optional[time]] = mapped_column(Time, nullable=True)
    new_pickup_end_time: Mapped[Optional[time]] = mapped_column(Time, nullable=True)
    new_close_time: Mapped[Optional[time]] = mapped_column(Time, nullable=True)
    new_is_open_enabled: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(),
    )

    operation_info: Mapped["StoreOperationInfo"] = relationship(
        "StoreOperationInfo", back_populates="modification",
    )

    __table_args__ = (
        CheckConstraint(
            "new_open_time < new_close_time", name="check_new_time_order",
        ),
        CheckConstraint(
            "new_pickup_start_time >= new_open_time AND new_pickup_start_time < new_close_time",
            name="check_new_pickup_start",
        ),
        CheckConstraint(
            "new_pickup_end_time > new_pickup_start_time AND new_pickup_end_time <= new_close_time",
            name="check_new_pickup_end",
        ),
        {"comment": "가게 운영 정보 변경 예약"},
    )
