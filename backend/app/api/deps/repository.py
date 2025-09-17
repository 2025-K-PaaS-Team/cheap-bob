from typing import Annotated

from fastapi import Depends

from api.deps.database import AsyncSessionDep
from repositories.store import StoreRepository
from repositories.store_product_info import StoreProductInfoRepository
from repositories.customer_detail import CustomerDetailRepository


def get_store_repository(session: AsyncSessionDep) -> StoreRepository:
    return StoreRepository(session)


def get_store_product_info_repository(session: AsyncSessionDep) -> StoreProductInfoRepository:
    return StoreProductInfoRepository(session)


def get_customer_detail_repository(session: AsyncSessionDep) -> CustomerDetailRepository:
    return CustomerDetailRepository(session)


StoreRepositoryDep = Annotated[StoreRepository, Depends(get_store_repository)]
StoreProductInfoRepositoryDep = Annotated[StoreProductInfoRepository, Depends(get_store_product_info_repository)]
CustomerDetailRepositoryDep = Annotated[CustomerDetailRepository, Depends(get_customer_detail_repository)]