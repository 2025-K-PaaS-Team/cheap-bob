from typing import Annotated

from fastapi import Depends

from api.deps.database import AsyncSessionDep
# 소비자
from repositories.customer import CustomerRepository
from repositories.customer_detail import CustomerDetailRepository
from repositories.customer_profile import CustomerProfileRepository
from repositories.customer_preferences import (
    CustomerPreferredMenuRepository,
    CustomerNutritionTypeRepository,
    CustomerAllergyRepository,
    CustomerToppingTypeRepository
)
from repositories.customer_favorite import CustomerFavoriteRepository
from repositories.customer_withdraw_reservation import CustomerWithdrawReservationRepository
# 판매자
from repositories.seller import SellerRepository
from repositories.seller_withdraw_reservation import SellerWithdrawReservationRepository
from repositories.store import StoreRepository
from repositories.store_image import StoreImageRepository
from repositories.store_address import StoreAddressRepository
from repositories.store_sns import StoreSNSRepository
from repositories.store_operation_info import StoreOperationInfoRepository
from repositories.store_operation_info_modification import StoreOperationInfoModificationRepository
from repositories.store_payment_info import StorePaymentInfoRepository
from repositories.store_product_info import StoreProductInfoRepository
from repositories.product_nutrition import ProductNutritionRepository
# 주문
from repositories.cart_item import CartItemRepository
from repositories.order_current_item import OrderCurrentItemRepository
from repositories.order_history_item import OrderHistoryItemRepository



# 소비자
def get_customer_repository(session: AsyncSessionDep) -> CustomerRepository:
    return CustomerRepository(session)

def get_customer_detail_repository(session: AsyncSessionDep) -> CustomerDetailRepository:
    return CustomerDetailRepository(session)


def get_customer_profile_repository(session: AsyncSessionDep) -> CustomerProfileRepository:
    return CustomerProfileRepository(session)


def get_customer_preferred_menu_repository(session: AsyncSessionDep) -> CustomerPreferredMenuRepository:
    return CustomerPreferredMenuRepository(session)


def get_customer_nutrition_type_repository(session: AsyncSessionDep) -> CustomerNutritionTypeRepository:
    return CustomerNutritionTypeRepository(session)


def get_customer_allergy_repository(session: AsyncSessionDep) -> CustomerAllergyRepository:
    return CustomerAllergyRepository(session)


def get_customer_topping_type_repository(session: AsyncSessionDep) -> CustomerToppingTypeRepository:
    return CustomerToppingTypeRepository(session)


def get_customer_favorite_repository(session: AsyncSessionDep) -> CustomerFavoriteRepository:
    return CustomerFavoriteRepository(session)


def get_customer_withdraw_reservation_repository() -> CustomerWithdrawReservationRepository:
    return CustomerWithdrawReservationRepository()


# 판매자
def get_seller_repository(session: AsyncSessionDep) -> SellerRepository:
    return SellerRepository(session)


def get_seller_withdraw_reservation_repository() -> SellerWithdrawReservationRepository:
    return SellerWithdrawReservationRepository()


def get_store_repository(session: AsyncSessionDep) -> StoreRepository:
    return StoreRepository(session)


def get_store_image_repository(session: AsyncSessionDep) -> StoreImageRepository:
    return StoreImageRepository(session)


def get_store_payment_info_repository(session: AsyncSessionDep) -> StorePaymentInfoRepository:
    return StorePaymentInfoRepository(session)


def get_store_address_repository(session: AsyncSessionDep) -> StoreAddressRepository:
    return StoreAddressRepository(session)


def get_store_sns_repository(session: AsyncSessionDep) -> StoreSNSRepository:
    return StoreSNSRepository(session)


def get_store_operation_info_repository(session: AsyncSessionDep) -> StoreOperationInfoRepository:
    return StoreOperationInfoRepository(session)


def get_store_operation_info_modification_repository(session: AsyncSessionDep) -> StoreOperationInfoModificationRepository:
    return StoreOperationInfoModificationRepository(session)


def get_product_nutrition_repository(session: AsyncSessionDep) -> ProductNutritionRepository:
    return ProductNutritionRepository(session)


def get_store_product_info_repository(session: AsyncSessionDep) -> StoreProductInfoRepository:
    return StoreProductInfoRepository(session)


# 주문
def get_cart_item_repository(session: AsyncSessionDep) -> CartItemRepository:
    return CartItemRepository(session)


def get_order_current_item_repository(session: AsyncSessionDep) -> OrderCurrentItemRepository:
    return OrderCurrentItemRepository(session)


def get_order_history_item_repository() -> OrderHistoryItemRepository:
    return OrderHistoryItemRepository()



# 소비자
CustomerRepositoryDep = Annotated[CustomerRepository, Depends(get_customer_repository)]
CustomerDetailRepositoryDep = Annotated[CustomerDetailRepository, Depends(get_customer_detail_repository)]
CustomerProfileRepositoryDep = Annotated[CustomerProfileRepository, Depends(get_customer_profile_repository)]
CustomerPreferredMenuRepositoryDep = Annotated[CustomerPreferredMenuRepository, Depends(get_customer_preferred_menu_repository)]
CustomerNutritionTypeRepositoryDep = Annotated[CustomerNutritionTypeRepository, Depends(get_customer_nutrition_type_repository)]
CustomerAllergyRepositoryDep = Annotated[CustomerAllergyRepository, Depends(get_customer_allergy_repository)]
CustomerToppingTypeRepositoryDep = Annotated[CustomerToppingTypeRepository, Depends(get_customer_topping_type_repository)]
CustomerFavoriteRepositoryDep = Annotated[CustomerFavoriteRepository, Depends(get_customer_favorite_repository)]
CustomerWithdrawReservationRepositoryDep = Annotated[CustomerWithdrawReservationRepository, Depends(get_customer_withdraw_reservation_repository)]
# 판매자
SellerRepositoryDep = Annotated[SellerRepository, Depends(get_seller_repository)]
StoreRepositoryDep = Annotated[StoreRepository, Depends(get_store_repository)]
SellerWithdrawReservationRepositoryDep = Annotated[SellerWithdrawReservationRepository, Depends(get_seller_withdraw_reservation_repository)]
StoreImageRepositoryDep = Annotated[StoreImageRepository, Depends(get_store_image_repository)]
StorePaymentInfoRepositoryDep = Annotated[StorePaymentInfoRepository, Depends(get_store_payment_info_repository)]
StoreAddressRepositoryDep = Annotated[StoreAddressRepository, Depends(get_store_address_repository)]
StoreSNSRepositoryDep = Annotated[StoreSNSRepository, Depends(get_store_sns_repository)]
StoreOperationInfoRepositoryDep = Annotated[StoreOperationInfoRepository, Depends(get_store_operation_info_repository)]
StoreOperationInfoModificationRepositoryDep = Annotated[StoreOperationInfoModificationRepository, Depends(get_store_operation_info_modification_repository)]
StoreProductInfoRepositoryDep = Annotated[StoreProductInfoRepository, Depends(get_store_product_info_repository)]
ProductNutritionRepositoryDep = Annotated[ProductNutritionRepository, Depends(get_product_nutrition_repository)]
# 주문
CartItemRepositoryDep = Annotated[CartItemRepository, Depends(get_cart_item_repository)]
OrderCurrentItemRepositoryDep = Annotated[OrderCurrentItemRepository, Depends(get_order_current_item_repository)]
OrderHistoryItemRepositoryDep = Annotated[OrderHistoryItemRepository, Depends(get_order_history_item_repository)]