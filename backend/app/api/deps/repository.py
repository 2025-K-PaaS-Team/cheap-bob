from typing import Annotated

from fastapi import Depends

from api.deps.database import AsyncSessionDep
from repositories.store import StoreRepository
from repositories.store_product_info import StoreProductInfoRepository
from repositories.customer_detail import CustomerDetailRepository
from repositories.customer_profile import CustomerProfileRepository
from repositories.order_current_item import OrderCurrentItemRepository
from repositories.store_payment_info import StorePaymentInfoRepository
from repositories.cart_item import CartItemRepository
from repositories.product_nutrition import ProductNutritionRepository
from repositories.customer_preferences import (
    CustomerPreferredMenuRepository,
    CustomerNutritionTypeRepository,
    CustomerAllergyRepository,
    CustomerToppingTypeRepository
)
from repositories.store_image import StoreImageRepository
from repositories.seller import SellerRepository
from repositories.store_address import StoreAddressRepository
from repositories.store_sns import StoreSNSRepository
from repositories.store_operation_info import StoreOperationInfoRepository
from repositories.customer_favorite import CustomerFavoriteRepository
from repositories.order_history_item import OrderHistoryItemRepository


def get_store_repository(session: AsyncSessionDep) -> StoreRepository:
    return StoreRepository(session)


def get_store_product_info_repository(session: AsyncSessionDep) -> StoreProductInfoRepository:
    return StoreProductInfoRepository(session)


def get_customer_detail_repository(session: AsyncSessionDep) -> CustomerDetailRepository:
    return CustomerDetailRepository(session)


def get_customer_profile_repository(session: AsyncSessionDep) -> CustomerProfileRepository:
    return CustomerProfileRepository(session)


def get_order_current_item_repository(session: AsyncSessionDep) -> OrderCurrentItemRepository:
    return OrderCurrentItemRepository(session)


def get_store_payment_info_repository(session: AsyncSessionDep) -> StorePaymentInfoRepository:
    return StorePaymentInfoRepository(session)


def get_cart_item_repository(session: AsyncSessionDep) -> CartItemRepository:
    return CartItemRepository(session)


def get_product_nutrition_repository(session: AsyncSessionDep) -> ProductNutritionRepository:
    return ProductNutritionRepository(session)


def get_customer_preferred_menu_repository(session: AsyncSessionDep) -> CustomerPreferredMenuRepository:
    return CustomerPreferredMenuRepository(session)


def get_customer_nutrition_type_repository(session: AsyncSessionDep) -> CustomerNutritionTypeRepository:
    return CustomerNutritionTypeRepository(session)


def get_customer_allergy_repository(session: AsyncSessionDep) -> CustomerAllergyRepository:
    return CustomerAllergyRepository(session)


def get_customer_topping_type_repository(session: AsyncSessionDep) -> CustomerToppingTypeRepository:
    return CustomerToppingTypeRepository(session)


def get_store_image_repository(session: AsyncSessionDep) -> StoreImageRepository:
    return StoreImageRepository(session)


def get_seller_repository(session: AsyncSessionDep) -> SellerRepository:
    return SellerRepository(session)


def get_address_repository(session: AsyncSessionDep) -> StoreAddressRepository:
    return StoreAddressRepository(session)


def get_store_sns_repository(session: AsyncSessionDep) -> StoreSNSRepository:
    return StoreSNSRepository(session)


def get_store_operation_info_repository(session: AsyncSessionDep) -> StoreOperationInfoRepository:
    return StoreOperationInfoRepository(session)


def get_customer_favorite_repository(session: AsyncSessionDep) -> CustomerFavoriteRepository:
    return CustomerFavoriteRepository(session)


def get_order_history_item_repository() -> OrderHistoryItemRepository:
    return OrderHistoryItemRepository()


StoreRepositoryDep = Annotated[StoreRepository, Depends(get_store_repository)]
StoreProductInfoRepositoryDep = Annotated[StoreProductInfoRepository, Depends(get_store_product_info_repository)]
CustomerDetailRepositoryDep = Annotated[CustomerDetailRepository, Depends(get_customer_detail_repository)]
CustomerProfileRepositoryDep = Annotated[CustomerProfileRepository, Depends(get_customer_profile_repository)]
OrderCurrentItemRepositoryDep = Annotated[OrderCurrentItemRepository, Depends(get_order_current_item_repository)]
StorePaymentInfoRepositoryDep = Annotated[StorePaymentInfoRepository, Depends(get_store_payment_info_repository)]
CartItemRepositoryDep = Annotated[CartItemRepository, Depends(get_cart_item_repository)]
ProductNutritionRepositoryDep = Annotated[ProductNutritionRepository, Depends(get_product_nutrition_repository)]
CustomerPreferredMenuRepositoryDep = Annotated[CustomerPreferredMenuRepository, Depends(get_customer_preferred_menu_repository)]
CustomerNutritionTypeRepositoryDep = Annotated[CustomerNutritionTypeRepository, Depends(get_customer_nutrition_type_repository)]
CustomerAllergyRepositoryDep = Annotated[CustomerAllergyRepository, Depends(get_customer_allergy_repository)]
CustomerToppingTypeRepositoryDep = Annotated[CustomerToppingTypeRepository, Depends(get_customer_topping_type_repository)]
StoreImageRepositoryDep = Annotated[StoreImageRepository, Depends(get_store_image_repository)]
SellerRepositoryDep = Annotated[SellerRepository, Depends(get_seller_repository)]
StoreAddressRepositoryDep = Annotated[StoreAddressRepository, Depends(get_address_repository)]
StoreSNSRepositoryDep = Annotated[StoreSNSRepository, Depends(get_store_sns_repository)]
StoreOperationInfoRepositoryDep = Annotated[StoreOperationInfoRepository, Depends(get_store_operation_info_repository)]
CustomerFavoriteRepositoryDep = Annotated[CustomerFavoriteRepository, Depends(get_customer_favorite_repository)]
OrderHistoryItemRepositoryDep = Annotated[OrderHistoryItemRepository, Depends(get_order_history_item_repository)]