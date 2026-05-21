from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.domain.auth.model.seller import Seller


class SellerRepository:
    def __init__(self, session: AsyncSession):
        self.session = session


    async def find_by_email(self, email: str) -> Optional[Seller]:
        return await self.session.get(Seller, email)


    async def exists_by_email(self, email: str) -> bool:
        stmt = select(Seller.email).where(Seller.email == email).limit(1)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None


    async def save(self, seller: Seller) -> Seller:
        self.session.add(seller)
        await self.session.flush()
        return seller


    async def delete_by_email(self, email: str) -> bool:
        """탈퇴 정리 worker 가 호출. Seller 의 관계 cascade 는 별도 (Store / Settlement 등은
        worker 가 따로 정리한 후 마지막에 본 메서드 호출)."""
        seller = await self.session.get(Seller, email)
        if seller is None:
            return False
        await self.session.delete(seller)
        await self.session.flush()
        return True
