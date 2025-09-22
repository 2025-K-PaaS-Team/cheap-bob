from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from database.models.customer import Customer


class CustomerProfileRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_all_profile_data(self, customer_email: str) -> Dict[str, Any]:
        """고객의 모든 프로필 데이터를 조회"""

        stmt = (
            select(Customer)
            .where(Customer.email == customer_email)
            .options(
                selectinload(Customer.detail),
                selectinload(Customer.preferred_menus),
                selectinload(Customer.nutrition_types),
                selectinload(Customer.allergies),
                selectinload(Customer.topping_types)
            )
        )
        
        result = await self.session.execute(stmt)
        customer = result.unique().scalar_one_or_none()
        
        return {
            "detail": customer.detail,
            "preferred_menus": customer.preferred_menus,
            "nutrition_types": customer.nutrition_types,
            "allergies": customer.allergies,
            "topping_types": customer.topping_types
        }