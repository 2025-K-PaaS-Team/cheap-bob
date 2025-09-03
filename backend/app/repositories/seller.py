from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.seller import Seller
from repositories.base import BaseRepository


class SellerRepository(BaseRepository[Seller]):
    def __init__(self, session: AsyncSession):
        super().__init__(Seller, session)
    
    async def get_by_email(self, email: str) -> Optional[Seller]:
        """이메일로 판매자 조회"""
        return await self.get_one(email=email)
    
    async def exists_by_email(self, email: str) -> bool:
        """이메일로 판매자 존재 여부 확인"""
        return await self.exists(email=email)