from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete, select

from app.domain.customer.model.customer_allergy import CustomerAllergy
from app.domain.customer.dto.preference import AllergyType


class CustomerAllergyRepository:
    def __init__(self, session: AsyncSession):
        self.session = session


    async def find_by_customer(self, customer_email: str) -> List[CustomerAllergy]:
        stmt = select(CustomerAllergy).where(
            CustomerAllergy.customer_email == customer_email,
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())


    async def save_bulk(
        self, customer_email: str, allergy_types: List[AllergyType],
    ) -> List[CustomerAllergy]:
        items = [
            CustomerAllergy(customer_email=customer_email, allergy_type=a)
            for a in allergy_types
        ]
        self.session.add_all(items)
        await self.session.flush()
        return items


    async def delete(self, customer_email: str, allergy_type: AllergyType) -> bool:
        stmt = delete(CustomerAllergy).where(
            CustomerAllergy.customer_email == customer_email,
            CustomerAllergy.allergy_type == allergy_type,
        )
        result = await self.session.execute(stmt)
        await self.session.flush()
        return result.rowcount > 0
