from typing import List, Optional, Tuple

from app.domain.seller.service.store_id_cache import SellerStoreIdCache
from app.domain.seller.service.exception import StoreNotFoundError
from app.domain.seller.repository.store_product_info import StoreProductInfoRepository
from app.domain.seller.repository.store import StoreRepository
from app.domain.seller.model.store_product_info import StoreProductInfo
from app.domain.seller.model.store import Store
from app.database.session import UnitOfWork, transactional


class SellerStoreReadService:
    """seller 도메인 가게 조회 — 다른 도메인 (customer search/favorite, auth registration_status) 도
    본 서비스만 호출한다. cross-domain repo 직접 import 를 금지하는 컨벤션 §18 의 진입점.
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
        from app.domain.seller.repository.store_operation_info import (
            StoreOperationInfoRepository,
        )
        return await StoreOperationInfoRepository(
            self._session,
        ).get_today_operation_info(store_id)


    @transactional
    async def list_with_products(
        self, *, offset: int, limit: int,
    ) -> Tuple[List[Store], bool]:
        """상품이 있는 가게 + 모든 관련 정보 eager-load. customer 검색용 — favorite 미포함."""
        items, is_end = await StoreRepository(
            self._session,
        ).get_stores_with_products_and_favorites(
            customer_email="",  # favorite 정보는 customer service 가 별도 결합한다.
            offset=offset,
            limit=limit,
        )
        # 위 메서드는 (Store, is_favorite) 튜플을 반환 — favorite 무시.
        return [s for s, _ in items], is_end


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
        items, is_end = await StoreRepository(
            self._session,
        ).search_by_location_with_favorites(
            sido=sido,
            sigungu=sigungu,
            bname=bname,
            customer_email="",
            offset=offset,
            limit=limit,
        )
        return [s for s, _ in items], is_end


    @transactional
    async def search_by_name(
        self, *, search_name: str, offset: int, limit: int,
    ) -> Tuple[List[Store], bool]:
        items, is_end = await StoreRepository(
            self._session,
        ).search_by_name_with_favorites(
            search_name, customer_email="", offset=offset, limit=limit,
        )
        return [s for s, _ in items], is_end


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
        items, is_end = await StoreRepository(
            self._session,
        ).search_by_location_and_name_with_favorites(
            sido=sido,
            sigungu=sigungu,
            bname=bname,
            search_name=search_name,
            customer_email="",
            offset=offset,
            limit=limit,
        )
        return [s for s, _ in items], is_end


    @transactional
    async def get_favorite_stores_by_customer(
        self, customer_email: str,
    ) -> List[Store]:
        """customer 가 즐겨찾기한 모든 가게 (full info eager-loaded).

        customer 도메인에서만 호출되는 cross-domain 진입점. customer_favorites 테이블 JOIN 은
        Store ORM 의 favorited_by relationship 으로 SQLAlchemy 가 처리한다.
        """
        return await StoreRepository(
            self._session,
        ).get_favorite_stores_with_full_info(customer_email)


    @transactional
    async def get_store_products_with_nutrition(
        self, store_id: str,
    ) -> List[StoreProductInfo]:
        return await StoreProductInfoRepository(
            self._session,
        ).get_by_store_with_nutrition(store_id)
