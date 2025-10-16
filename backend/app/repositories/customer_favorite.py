from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, and_
from repositories.base import BaseRepository
from database.models.customer_favorite import CustomerFavorite


class CustomerFavoriteRepository(BaseRepository[CustomerFavorite]):
    def __init__(self, session: AsyncSession):
        super().__init__(CustomerFavorite, session)
    
    async def get_by_customer_and_store(self, customer_email: str, store_id: str) -> Optional[CustomerFavorite]:
        """특정 소비자과 가게의 즐겨찾기 조회"""
        result = await self.session.execute(
            select(self.model).where(
                and_(
                    self.model.customer_email == customer_email,
                    self.model.store_id == store_id
                )
            )
        )
        return result.scalar_one_or_none()
    
    async def create_for_customer(self, customer_email: str, store_id: str) -> CustomerFavorite:
        """소비자의 즐겨찾기 추가"""
        return await self.create(
            customer_email=customer_email,
            store_id=store_id
        )
    
    async def delete_for_customer(self, customer_email: str, store_id: str) -> bool:
        """소비자의 특정 가게 즐겨찾기 삭제"""
        result = await self.session.execute(
            delete(self.model).where(
                and_(
                    self.model.customer_email == customer_email,
                    self.model.store_id == store_id
                )
            )
        )
        await self.session.flush()
        return result.rowcount > 0