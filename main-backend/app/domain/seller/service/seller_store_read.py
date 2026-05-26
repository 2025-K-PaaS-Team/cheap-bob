from typing import List, Optional, Tuple

from app.domain.seller.service.store_id_cache import SellerStoreIdCache
from app.domain.seller.service.exception import StoreNotFoundError
from app.domain.seller.repository.store_product_info import StoreProductInfoRepository
from app.domain.seller.repository.store_operation_info import (
    StoreOperationInfoRepository,
)
from app.domain.seller.repository.store import StoreRepository
from app.domain.seller.model.store_product_info import StoreProductInfo
from app.domain.seller.model.store import Store
from app.database.session import UnitOfWork, transactional


class SellerStoreReadService:
    """seller 도메인 가게 조회 — 다른 도메인 (customer search/favorite, auth registration_status) 도 본 서비스만 호출한다.
    """

    def __init__(self, uow: UnitOfWork):
        self.uow = uow


    @transactional
    async def get_store_id_by_seller_email(self, seller_email: str) -> str:
        """Redis 캐시 후 DB. 가게가 없으면 `StoreNotFoundError`."""
        cached = await SellerStoreIdCache.get(seller_email)
        if cached:
            return cached

        stores = await StoreRepository(self._session).get_by_seller_email(seller_email)
        if not stores:
            raise StoreNotFoundError("가게를 찾을 수 없습니다.")

        store_id = stores[0].store_id
        await SellerStoreIdCache.set(seller_email, store_id)
        return store_id


    @transactional
    async def get_with_full_info(self, store_id: str) -> Optional[Store]:
        return await StoreRepository(self._session).get_with_full_info(store_id)


    @transactional
    async def get_today_operation(self, store_id: str):
        """오늘 요일의 가게 운영 정보. payment 의 영업 / 픽업 시간 검증에 사용."""
        return await StoreOperationInfoRepository(
            self._session,
        ).get_today_operation_info(store_id)


    @transactional
    async def list_with_products(
        self, *, offset: int, limit: int,
    ) -> Tuple[List[Store], bool]:
        """상품이 있는 가게 + 모든 관련 정보 eager-load. favorite 결합은 customer service 책임."""
        return await StoreRepository(self._session).list_with_products_paginated(
            offset=offset, limit=limit,
        )


    @transactional
    async def search_by_location(
        self,
        *,
        sido: str,
        sigungu: str,
        bname: List[str],
        offset: int,
        limit: int,
    ) -> Tuple[List[Store], bool]:
        return await StoreRepository(self._session).search_by_location_paginated(
            sido=sido, sigungu=sigungu, bname=bname, offset=offset, limit=limit,
        )


    @transactional
    async def search_by_name(
        self, *, search_name: str, offset: int, limit: int,
    ) -> Tuple[List[Store], bool]:
        return await StoreRepository(self._session).search_by_name_paginated(
            search_name=search_name, offset=offset, limit=limit,
        )


    @transactional
    async def search_by_location_and_name(
        self,
        *,
        sido: str,
        sigungu: str,
        bname: List[str],
        search_name: str,
        offset: int,
        limit: int,
    ) -> Tuple[List[Store], bool]:
        return await StoreRepository(self._session).search_by_location_and_name_paginated(
            sido=sido,
            sigungu=sigungu,
            bname=bname,
            search_name=search_name,
            offset=offset,
            limit=limit,
        )


    @transactional
    async def get_by_store_ids(self, store_ids: List[str]) -> List[Store]:
        """주어진 store_id 목록을 모든 관련 정보와 함께 조회. customer favorite 결합용."""
        return await StoreRepository(self._session).get_by_store_ids(store_ids)


    @transactional
    async def get_store_products_with_nutrition(
        self, store_id: str,
    ) -> List[StoreProductInfo]:
        return await StoreProductInfoRepository(
            self._session,
        ).get_by_store_with_nutrition(store_id)
