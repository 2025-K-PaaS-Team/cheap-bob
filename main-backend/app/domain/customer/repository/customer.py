from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.customer.model.customer import Customer


class CustomerRepository:
    def __init__(self, session: AsyncSession):
        self.session = session


    async def find_by_email(self, email: str) -> Optional[Customer]:
        return await self.session.get(Customer, email)


    async def save(self, customer: Customer) -> Customer:
        self.session.add(customer)
        await self.session.flush()
        return customer


    async def delete_by_email(self, email: str) -> bool:
        """탈퇴 정리 worker 가 호출. `Customer.relationships` 의 cascade='all, delete-orphan'
        설정에 의해 detail / favorite / 4종 preference 가 함께 삭제된다.

        Returns: 실제 삭제됐으면 True, 대상이 없었으면 False.
        """
        customer = await self.session.get(Customer, email)
        if customer is None:
            return False
        await self.session.delete(customer)
        await self.session.flush()
        return True
