from typing import TYPE_CHECKING, Optional
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, Integer, String

from app.database.session import Base


if TYPE_CHECKING:
    from app.domain.seller.model.store import Store
    from app.domain.seller.model.product_nutrition import ProductNutrition
    from app.domain.order.model.order_current_item import OrderCurrentItem
    from app.domain.order.model.cart_item import CartItem


class StoreProductInfo(Base):
    """가게 상품 정보. 재고는 (initial - purchased + admin_adjustment) 식으로 계산된다."""

    __tablename__ = "store_product_info"
    __mapper_args__ = {"eager_defaults": True}

    product_id: Mapped[str] = mapped_column(String(255), primary_key=True)
    store_id: Mapped[str] = mapped_column(
        String(255), ForeignKey("stores.store_id"),
    )
    product_name: Mapped[str] = mapped_column(String(255))
    description: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    initial_stock: Mapped[int] = mapped_column(Integer)
    purchased_quantity: Mapped[int] = mapped_column(Integer, default=0)
    admin_adjustment: Mapped[int] = mapped_column(Integer, default=0)
    price: Mapped[int] = mapped_column(Integer)
    sale: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    version: Mapped[int] = mapped_column(Integer, default=1)

    store: Mapped["Store"] = relationship("Store", back_populates="products")
    cart_items: Mapped[list["CartItem"]] = relationship(
        "CartItem", back_populates="product",
    )
    order_current_items: Mapped[list["OrderCurrentItem"]] = relationship(
        "OrderCurrentItem", back_populates="product",
    )
    nutrition_info: Mapped[list["ProductNutrition"]] = relationship(
        "ProductNutrition", back_populates="product", cascade="all, delete-orphan",
    )


    @property
    def current_stock(self) -> int:
        """현재 재고 = 초기 재고 - 구매 수량 + 판매자 조절."""
        return self.initial_stock - self.purchased_quantity + self.admin_adjustment
