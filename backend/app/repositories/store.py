from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.store import Store
from repositories.base import BaseRepository


class StoreRepository(BaseRepository[Store]):
    """가게"""
    def __init__(self, session: AsyncSession):
        super().__init__(Store, session)
    
    async def get_by_store_id(self, store_id: str) -> Optional[Store]:
        """가게 ID로 조회"""
        return await self.get_by_pk(store_id)
    
    async def get_by_seller_email(self, seller_email: str) -> List[Store]:
        """판매자 이메일로 가게 목록 조회"""
        return await self.get_many(
            filters={"seller_email": seller_email},
            order_by=["-created_at"]
        )
    
    async def get_all_with_relations(self) -> List[Store]:
        """모든 가게를 관계 데이터와 함께 조회"""
        return await self.get_many(
            order_by=["-created_at"],
            load_relations=["seller", "location", "payment_info", "products"]
        )
    
    async def search_by_name(self, keyword: str) -> List[Store]:
        """가게 이름으로 검색"""
        return await self.get_many(
            filters={"store_name": {"like": keyword}},
            order_by=["store_name"]
        )