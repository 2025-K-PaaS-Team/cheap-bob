from typing import TYPE_CHECKING, Optional
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String

from app.database.session import Base


if TYPE_CHECKING:
    from app.domain.seller.model.store import Store


class StoreAddress(Base):
    """가게 주소 정보 (시/도, 시/군/구, 읍/면/동, 좌표, 가까운 역)."""

    __tablename__ = "store_addresses"
    __mapper_args__ = {"eager_defaults": True}

    address_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    sido: Mapped[str] = mapped_column(String(50))
    sigungu: Mapped[str] = mapped_column(String(50))
    bname: Mapped[str] = mapped_column(String(50))
    lat: Mapped[str] = mapped_column(String(50))
    lng: Mapped[str] = mapped_column(String(50))
    nearest_station: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    walking_time: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    stores: Mapped[list["Store"]] = relationship("Store", back_populates="address")
