from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete, select

from app.domain.customer.model.customer_preferred_menu import CustomerPreferredMenu
from app.domain.customer.dto.preference import PreferredMenu


class CustomerPreferredMenuRepository:
    def __init__(self, session: AsyncSession):
        self.session = session


    async def find_by_customer(self, customer_email: str) -> List[CustomerPreferredMenu]:
        stmt = select(CustomerPreferredMenu).where(
            CustomerPreferredMenu.customer_email == customer_email,
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())


    async def save_bulk(
        self, customer_email: str, menu_types: List[PreferredMenu],
    ) -> List[CustomerPreferredMenu]:
        items = [
            CustomerPreferredMenu(customer_email=customer_email, menu_type=m)
            for m in menu_types
        ]
        self.session.add_all(items)
        await self.session.flush()
        return items


    async def delete(self, customer_email: str, menu_type: PreferredMenu) -> bool:
        stmt = delete(CustomerPreferredMenu).where(
            CustomerPreferredMenu.customer_email == customer_email,
            CustomerPreferredMenu.menu_type == menu_type,
        )
        result = await self.session.execute(stmt)
        await self.session.flush()
        return result.rowcount > 0
