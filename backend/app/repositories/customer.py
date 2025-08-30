from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.customer import Customer
from repositories.base import BaseRepository


class CustomerRepository(BaseRepository[Customer]):
    def __init__(self, session: AsyncSession):
        super().__init__(Customer, session)
    
    async def get_by_email(self, email: str) -> Optional[Customer]:
        """이메일로 고객 조회"""
        return await self.get_one(email=email)
    
    async def exists_by_email(self, email: str) -> bool:
        """이메일로 고객 존재 여부 확인"""
        return await self.exists(email=email)