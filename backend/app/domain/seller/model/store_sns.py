from typing import TYPE_CHECKING, Optional
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, Integer, String, Text

from app.database.session import Base


if TYPE_CHECKING:
    from app.domain.seller.model.store import Store


class StoreSNS(Base):
    """가게 SNS 정보 (Instagram / Facebook / X / Homepage URL)."""

    __tablename__ = "store_sns"
    __mapper_args__ = {"eager_defaults": True}

    sns_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    store_id: Mapped[str] = mapped_column(
        String(255), ForeignKey("stores.store_id"), unique=True,
    )

    instagram: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    facebook: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    x: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    homepage: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    store: Mapped["Store"] = relationship("Store", back_populates="sns_info")
