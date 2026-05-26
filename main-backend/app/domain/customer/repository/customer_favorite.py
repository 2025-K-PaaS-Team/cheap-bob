from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete, select

from app.domain.customer.model.customer_favorite import CustomerFavorite


class CustomerFavoriteRepository:
    def __init__(self, session: AsyncSession):
        self.session = session


    async def find_by_customer_and_store(
        self, customer_email: str, store_id: str,
    ) -> Optional[CustomerFavorite]:
        stmt = select(CustomerFavorite).where(
            CustomerFavorite.customer_email == customer_email,
            CustomerFavorite.store_id == store_id,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()


    async def find_store_ids_by_customer(self, customer_email: str) -> set[str]:
        """customer 가 즐겨찾기한 모든 store_id 집합. search 결과 데코레이션에 사용."""
        stmt = select(CustomerFavorite.store_id).where(
            CustomerFavorite.customer_email == customer_email,
        )
        result = await self.session.execute(stmt)
        return {row for row in result.scalars().all()}


    async def save(self, customer_email: str, store_id: str) -> CustomerFavorite:
        favorite = CustomerFavorite(customer_email=customer_email, store_id=store_id)
        self.session.add(favorite)
        await self.session.flush()
        return favorite


    async def delete(self, customer_email: str, store_id: str) -> bool:
        stmt = delete(CustomerFavorite).where(
            CustomerFavorite.customer_email == customer_email,
            CustomerFavorite.store_id == store_id,
        )
        result = await self.session.execute(stmt)
        await self.session.flush()
        return result.rowcount > 0
