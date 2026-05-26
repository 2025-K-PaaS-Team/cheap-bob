from typing import TYPE_CHECKING, Optional
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from datetime import datetime

from app.database.session import Base


if TYPE_CHECKING:
    from app.domain.seller.model.store_sns import StoreSNS
    from app.domain.seller.model.store_product_info import StoreProductInfo
    from app.domain.seller.model.store_operation_info import StoreOperationInfo
    from app.domain.seller.model.store_image import StoreImage
    from app.domain.seller.model.store_address import StoreAddress
    from app.domain.seller.model.seller import Seller
    from app.domain.customer.model.customer_favorite import CustomerFavorite


class Store(Base):
    """가게."""

    __tablename__ = "stores"
    __mapper_args__ = {"eager_defaults": True}

    store_id: Mapped[str] = mapped_column(String(255), primary_key=True)
    store_name: Mapped[str] = mapped_column(String(255))
    seller_email: Mapped[str] = mapped_column(
        String(255), ForeignKey("sellers.email"),
    )

    store_introduction: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    store_phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    store_postal_code: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    store_address: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    store_detail_address: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    address_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("store_addresses.address_id"), nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(),
    )

    # 관계는 모두 string 기반이라 도메인 경계를 코드 import 로 깨지 않는다.
    seller: Mapped["Seller"] = relationship("Seller", backref="stores")
    address: Mapped[Optional["StoreAddress"]] = relationship(
        "StoreAddress", back_populates="stores",
    )
    products: Mapped[list["StoreProductInfo"]] = relationship(
        "StoreProductInfo", back_populates="store",
    )
    sns_info: Mapped[Optional["StoreSNS"]] = relationship(
        "StoreSNS", back_populates="store", uselist=False,
    )
    images: Mapped[list["StoreImage"]] = relationship(
        "StoreImage", back_populates="store", cascade="all, delete-orphan",
    )
    operation_info: Mapped[list["StoreOperationInfo"]] = relationship(
        "StoreOperationInfo", back_populates="store", cascade="all, delete-orphan",
    )
    favorited_by: Mapped[list["CustomerFavorite"]] = relationship(
        "CustomerFavorite", back_populates="store", cascade="all, delete-orphan",
    )
    # payment 도메인 분리 — store_payment_info 는 backend-payment 가 소유. 관계 제거.
