from typing import TYPE_CHECKING, Optional
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Boolean, DateTime, String
from datetime import datetime

from app.database.session import Base


if TYPE_CHECKING:
    from app.domain.customer.model.customer_topping_type import CustomerToppingType
    from app.domain.customer.model.customer_preferred_menu import CustomerPreferredMenu
    from app.domain.customer.model.customer_nutrition_type import CustomerNutritionType
    from app.domain.customer.model.customer_favorite import CustomerFavorite
    from app.domain.customer.model.customer_detail import CustomerDetail
    from app.domain.customer.model.customer_allergy import CustomerAllergy


class Customer(Base):
    """소비자 계정. email 이 인증 principal 이자 PK.

    원래 auth 도메인에 있었으나 customer 측 4종 선호 + detail + favorite 와의 관계가
    모두 본 모델에서 출발하므로 customer 도메인 소유로 정리. auth 는 OAuth/JWT 전담.
    """

    __tablename__ = "customers"
    __mapper_args__ = {"eager_defaults": True}

    email: Mapped[str] = mapped_column(String(255), primary_key=True, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(),
    )

    detail: Mapped[Optional["CustomerDetail"]] = relationship(
        "CustomerDetail",
        back_populates="customer",
        uselist=False,
        cascade="all, delete-orphan",
    )
    preferred_menus: Mapped[list["CustomerPreferredMenu"]] = relationship(
        "CustomerPreferredMenu",
        back_populates="customer",
        cascade="all, delete-orphan",
    )
    nutrition_types: Mapped[list["CustomerNutritionType"]] = relationship(
        "CustomerNutritionType",
        back_populates="customer",
        cascade="all, delete-orphan",
    )
    allergies: Mapped[list["CustomerAllergy"]] = relationship(
        "CustomerAllergy",
        back_populates="customer",
        cascade="all, delete-orphan",
    )
    topping_types: Mapped[list["CustomerToppingType"]] = relationship(
        "CustomerToppingType",
        back_populates="customer",
        cascade="all, delete-orphan",
    )
    favorites: Mapped[list["CustomerFavorite"]] = relationship(
        "CustomerFavorite",
        back_populates="customer",
        cascade="all, delete-orphan",
    )
