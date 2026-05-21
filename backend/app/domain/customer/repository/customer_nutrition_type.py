from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete, select

from app.domain.seller.dto.nutrition import NutritionType
from app.domain.customer.model.customer_nutrition_type import CustomerNutritionType


class CustomerNutritionTypeRepository:
    def __init__(self, session: AsyncSession):
        self.session = session


    async def find_by_customer(
        self, customer_email: str,
    ) -> List[CustomerNutritionType]:
        stmt = select(CustomerNutritionType).where(
            CustomerNutritionType.customer_email == customer_email,
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())


    async def save_bulk(
        self, customer_email: str, nutrition_types: List[NutritionType],
    ) -> List[CustomerNutritionType]:
        items = [
            CustomerNutritionType(customer_email=customer_email, nutrition_type=n)
            for n in nutrition_types
        ]
        self.session.add_all(items)
        await self.session.flush()
        return items


    async def delete(
        self, customer_email: str, nutrition_type: NutritionType,
    ) -> bool:
        stmt = delete(CustomerNutritionType).where(
            CustomerNutritionType.customer_email == customer_email,
            CustomerNutritionType.nutrition_type == nutrition_type,
        )
        result = await self.session.execute(stmt)
        await self.session.flush()
        return result.rowcount > 0
