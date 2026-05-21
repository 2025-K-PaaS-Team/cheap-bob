from typing import Optional
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.domain.auth.model.customer import Customer


class CustomerProfileRepository:
    """전체 프로필 (detail + 4종 선호) 을 한 번에 eager-load 한다."""

    def __init__(self, session: AsyncSession):
        self.session = session


    async def find_full_profile(self, customer_email: str) -> Optional[Customer]:
        stmt = (
            select(Customer)
            .where(Customer.email == customer_email)
            .options(
                selectinload(Customer.detail),
                selectinload(Customer.preferred_menus),
                selectinload(Customer.nutrition_types),
                selectinload(Customer.allergies),
                selectinload(Customer.topping_types),
            )
        )
        result = await self.session.execute(stmt)
        return result.unique().scalar_one_or_none()
