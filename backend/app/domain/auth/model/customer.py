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
    __tablename__ = "customers"
    __mapper_args__ = {"eager_defaults": True}

    email: Mapped[str] = mapped_column(String(255), primary_key=True, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(),
    )

    # 관계는 string 이름 기반이라 customer 도메인의 모델 파일을 직접 import 하지 않는다.
    # 도메인 경계는 코드 import 기준으로만 본다는 컨벤션 §18 의 원칙과 충돌하지 않는다.
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
