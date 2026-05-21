from typing import List, Tuple

from app.domain.seller.service.store_utils import convert_store_to_response
from app.domain.seller.service.seller_store_read import SellerStoreReadService
from app.domain.seller.schema.store import (
    PaginatedStoreResponse,
    StoreDetailResponseForCustomer,
)
from app.domain.seller.schema.product import ProductResponse, ProductsResponse
from app.domain.customer.service.exception import StoreNotFoundError
from app.domain.customer.service.customer_history import CustomerHistoryService
from app.domain.customer.repository.customer_favorite import CustomerFavoriteRepository
from app.database.session import UnitOfWork, transactional


_PAGE_SIZE = 4


class CustomerSearchService:
    """소비자의 가게/상품 검색.

    가게 데이터는 seller 도메인의 `SellerStoreReadService` 를 통해서만 접근한다 (strict
    service-to-service). 즐겨찾기 정보는 customer 자신의 `CustomerFavoriteRepository` 에서
    별도 조회 후 in-memory 결합한다.
    """

    def __init__(
        self,
        uow: UnitOfWork,
        history_service: CustomerHistoryService,
        seller_store_read_service: SellerStoreReadService,
    ):
        self.uow = uow
        self.history_service = history_service
        self.seller_store_read_service = seller_store_read_service


    async def list_stores(
        self, *, customer_email: str, page: int,
    ) -> PaginatedStoreResponse:
        offset = page * _PAGE_SIZE
        stores, is_end = await self.seller_store_read_service.list_with_products(
            offset=offset, limit=_PAGE_SIZE,
        )
        favorite_ids = await self._favorite_store_ids(customer_email)
        return PaginatedStoreResponse(
            stores=[
                convert_store_to_response(s, s.store_id in favorite_ids)
                for s in stores
            ],
            is_end=is_end,
        )


    async def get_store_products(self, store_id: str) -> ProductsResponse:
        store = await self.seller_store_read_service.get_with_full_info(store_id)
        if store is None:
            raise StoreNotFoundError("가게를 찾을 수 없습니다")

        products = await self.seller_store_read_service.get_store_products_with_nutrition(
            store_id,
        )
        return ProductsResponse(
            store_id=store.store_id,
            store_name=store.store_name,
            products=[
                ProductResponse(
                    product_id=p.product_id,
                    store_id=p.store_id,
                    product_name=p.product_name,
                    description=p.description,
                    initial_stock=p.initial_stock,
                    current_stock=p.current_stock,
                    price=p.price,
                    sale=p.sale,
                    version=p.version,
                    nutrition_types=[
                        info.nutrition_type for info in (p.nutrition_info or [])
                    ],
                )
                for p in products
            ],
        )


    async def search_by_location(
        self,
        *,
        customer_email: str,
        sido: str,
        sigungu: str,
        bname: List[str],
        page: int,
    ) -> PaginatedStoreResponse:
        offset = page * _PAGE_SIZE
        stores, is_end = await self.seller_store_read_service.search_by_location(
            sido=sido, sigungu=sigungu, bname=bname,
            offset=offset, limit=_PAGE_SIZE,
        )
        favorite_ids = await self._favorite_store_ids(customer_email)
        return PaginatedStoreResponse(
            stores=[
                convert_store_to_response(s, s.store_id in favorite_ids)
                for s in stores
            ],
            is_end=is_end,
        )


    async def search_by_name(
        self, *, customer_email: str, search_name: str, page: int,
    ) -> Tuple[PaginatedStoreResponse, str]:
        offset = page * _PAGE_SIZE
        stores, is_end = await self.seller_store_read_service.search_by_name(
            search_name=search_name, offset=offset, limit=_PAGE_SIZE,
        )
        favorite_ids = await self._favorite_store_ids(customer_email)
        return PaginatedStoreResponse(
            stores=[
                convert_store_to_response(s, s.store_id in favorite_ids)
                for s in stores
            ],
            is_end=is_end,
        ), search_name


    async def search_by_location_and_name(
        self,
        *,
        customer_email: str,
        sido: str,
        sigungu: str,
        bname: List[str],
        search_name: str,
        page: int,
    ) -> Tuple[PaginatedStoreResponse, str]:
        offset = page * _PAGE_SIZE
        stores, is_end = await self.seller_store_read_service.search_by_location_and_name(
            sido=sido,
            sigungu=sigungu,
            bname=bname,
            search_name=search_name,
            offset=offset,
            limit=_PAGE_SIZE,
        )
        favorite_ids = await self._favorite_store_ids(customer_email)
        return PaginatedStoreResponse(
            stores=[
                convert_store_to_response(s, s.store_id in favorite_ids)
                for s in stores
            ],
            is_end=is_end,
        ), search_name


    async def list_favorite_stores(
        self, customer_email: str,
    ) -> List[StoreDetailResponseForCustomer]:
        stores = await self.seller_store_read_service.get_favorite_stores_by_customer(
            customer_email,
        )
        return [convert_store_to_response(s, is_favorite=True) for s in stores]


    @transactional
    async def _favorite_store_ids(self, customer_email: str) -> set[str]:
        return await CustomerFavoriteRepository(
            self._session,
        ).find_store_ids_by_customer(customer_email)
