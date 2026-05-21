from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete, select

from app.domain.customer.model.customer_topping_type import CustomerToppingType
from app.domain.customer.dto.preference import ToppingType


class CustomerToppingTypeRepository:
    def __init__(self, session: AsyncSession):
        self.session = session


    async def find_by_customer(self, customer_email: str) -> List[CustomerToppingType]:
        stmt = select(CustomerToppingType).where(
            CustomerToppingType.customer_email == customer_email,
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())


    async def save_bulk(
        self, customer_email: str, topping_types: List[ToppingType],
    ) -> List[CustomerToppingType]:
        items = [
            CustomerToppingType(customer_email=customer_email, topping_type=t)
            for t in topping_types
        ]
        self.session.add_all(items)
        await self.session.flush()
        return items


    async def delete(self, customer_email: str, topping_type: ToppingType) -> bool:
        stmt = delete(CustomerToppingType).where(
            CustomerToppingType.customer_email == customer_email,
            CustomerToppingType.topping_type == topping_type,
        )
        result = await self.session.execute(stmt)
        await self.session.flush()
        return result.rowcount > 0
