from typing import List, Optional
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_

from app.domain.seller.model.store_product_info import StoreProductInfo
from app.domain.seller.model.store_address import StoreAddress
from app.domain.seller.model.store import Store
from app.database.postgresql_repository import BaseRepository


_FULL_RELATIONS = (
    "address",
    "sns_info",
    "operation_info",
    "images",
)


class StoreRepository(BaseRepository[Store]):
    """가게 CRUD + 검색. 본 repository 는 seller 도메인 모델만 참조한다

    cross-domain 결합 (favorite / order / payment) 은 호출하는 service 계층에서 service-to-service
    로 처리한다.
    """

    def __init__(self, session: AsyncSession):
        super().__init__(Store, session)


    async def get_by_store_id(self, store_id: str) -> Optional[Store]:
        return await self.get_by_pk(store_id)


    async def get_by_seller_email(self, seller_email: str) -> List[Store]:
        return await self.get_many(
            filters={"seller_email": seller_email},
            order_by=["-created_at"],
        )


    async def get_with_address(self, store_id: str) -> Optional[Store]:
        query = (
            select(Store)
            .options(selectinload(Store.address))
            .where(Store.store_id == store_id)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()


    async def get_with_full_info(self, store_id: str) -> Optional[Store]:
        # payment_info 는 MSA 분리로 backend-payment 가 소유 — 필요한 caller 는
        # InternalPaymentClient 로 별도 조회한다.
        query = (
            select(Store)
            .options(
                *(selectinload(getattr(Store, rel)) for rel in _FULL_RELATIONS),
                selectinload(Store.seller),
                selectinload(Store.products).selectinload(StoreProductInfo.nutrition_info),
            )
            .where(Store.store_id == store_id)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()


    async def get_by_store_ids(self, store_ids: List[str]) -> List[Store]:
        """주어진 store_id 목록을 모든 관련 정보와 함께 조회 (customer favorite 결합용)."""
        if not store_ids:
            return []
        query = (
            select(Store)
            .where(Store.store_id.in_(store_ids))
            .options(
                *(selectinload(getattr(Store, rel)) for rel in _FULL_RELATIONS),
                selectinload(Store.products).selectinload(StoreProductInfo.nutrition_info),
            )
        )
        result = await self.session.execute(query)
        return result.scalars().unique().all()


    async def list_with_products_paginated(
        self, *, offset: int, limit: int,
    ) -> tuple[List[Store], bool]:
        """상품이 1개 이상인 가게를 페이지네이션해 반환. (stores, is_end)."""
        query = (
            self._base_search_query()
            .order_by(Store.created_at.desc())
            .offset(offset)
            .limit(limit + 1)
        )
        return await self._fetch_paginated(query, limit)


    async def search_by_location_paginated(
        self,
        *,
        sido: str,
        sigungu: str,
        bname: List[str],
        offset: int,
        limit: int,
    ) -> tuple[List[Store], bool]:
        query = (
            self._base_search_query()
            .join(Store.address)
            .where(
                and_(
                    StoreAddress.sido == sido,
                    StoreAddress.sigungu == sigungu,
                    StoreAddress.bname.in_(bname),
                ),
            )
            .order_by(Store.store_name)
            .offset(offset)
            .limit(limit + 1)
        )
        return await self._fetch_paginated(query, limit)


    async def search_by_name_paginated(
        self, *, search_name: str, offset: int, limit: int,
    ) -> tuple[List[Store], bool]:
        query = (
            self._base_search_query()
            .where(
                or_(
                    Store.store_name.like(f"%{search_name}%"),
                    StoreProductInfo.product_name.like(f"%{search_name}%"),
                ),
            )
            .order_by(Store.store_name)
            .offset(offset)
            .limit(limit + 1)
        )
        return await self._fetch_paginated(query, limit)


    async def search_by_location_and_name_paginated(
        self,
        *,
        sido: str,
        sigungu: str,
        bname: List[str],
        search_name: str,
        offset: int,
        limit: int,
    ) -> tuple[List[Store], bool]:
        query = (
            self._base_search_query()
            .join(Store.address)
            .where(
                and_(
                    StoreAddress.sido == sido,
                    StoreAddress.sigungu == sigungu,
                    StoreAddress.bname.in_(bname),
                    or_(
                        Store.store_name.like(f"%{search_name}%"),
                        StoreProductInfo.product_name.like(f"%{search_name}%"),
                    ),
                ),
            )
            .order_by(Store.store_name)
            .offset(offset)
            .limit(limit + 1)
        )
        return await self._fetch_paginated(query, limit)


    def _base_search_query(self):
        """상품이 있는 가게에 대한 공통 SELECT. INNER JOIN with products + full eager-load."""
        return (
            select(Store)
            .join(Store.products)
            .options(
                *(selectinload(getattr(Store, rel)) for rel in _FULL_RELATIONS),
                selectinload(Store.products).selectinload(StoreProductInfo.nutrition_info),
            )
            .distinct()
        )


    async def _fetch_paginated(
        self, query, limit: int,
    ) -> tuple[List[Store], bool]:
        result = await self.session.execute(query)
        rows = result.scalars().unique().all()
        has_next = len(rows) > limit
        return list(rows[:limit]), not has_next
