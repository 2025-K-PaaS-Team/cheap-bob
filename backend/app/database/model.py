"""Alembic 자동 감지 용 모델 집계.

`migration/env.py` 가 이 모듈만 import 하면 `Base.metadata` 에 모든 도메인의 ORM 모델이 등록된다.
"""

from app.domain.seller.model.store_sns import StoreSNS
from app.domain.seller.model.store_product_info import StoreProductInfo
from app.domain.seller.model.store_operation_info_modification import (
    StoreOperationInfoModification,
)
from app.domain.seller.model.store_operation_info import StoreOperationInfo
from app.domain.seller.model.store_image import StoreImage
from app.domain.seller.model.store_address import StoreAddress
from app.domain.seller.model.store import Store
from app.domain.seller.model.seller import Seller
from app.domain.seller.model.product_nutrition import ProductNutrition
from app.domain.order.model.order_current_item import OrderCurrentItem
from app.domain.customer.model.customer_topping_type import CustomerToppingType
from app.domain.customer.model.customer_preferred_menu import CustomerPreferredMenu
from app.domain.customer.model.customer_nutrition_type import CustomerNutritionType
from app.domain.customer.model.customer_favorite import CustomerFavorite
from app.domain.customer.model.customer_detail import CustomerDetail
from app.domain.customer.model.customer_allergy import CustomerAllergy
from app.domain.customer.model.customer import Customer


__all__ = [
    "Customer",
    "Seller",
    "CustomerDetail",
    "CustomerFavorite",
    "CustomerAllergy",
    "CustomerNutritionType",
    "CustomerPreferredMenu",
    "CustomerToppingType",
    "Store",
    "StoreAddress",
    "StoreImage",
    "StoreSNS",
    "StoreOperationInfo",
    "StoreOperationInfoModification",
    "StoreProductInfo",
    "ProductNutrition",
    "OrderCurrentItem",
]
