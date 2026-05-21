from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.customer.model.customer_detail import CustomerDetail


class CustomerDetailRepository:
    def __init__(self, session: AsyncSession):
        self.session = session


    async def find_by_customer(self, customer_email: str) -> Optional[CustomerDetail]:
        return await self.session.get(CustomerDetail, customer_email)


    async def exists_by_customer(self, customer_email: str) -> bool:
        return await self.find_by_customer(customer_email) is not None


    async def save(self, detail: CustomerDetail) -> CustomerDetail:
        self.session.add(detail)
        await self.session.flush()
        return detail


    async def update(
        self,
        customer_email: str,
        *,
        nickname: Optional[str] = None,
        phone_number: Optional[str] = None,
    ) -> Optional[CustomerDetail]:
        """nickname / phone_number 중 None 이 아닌 값만 갱신한다."""
        detail = await self.find_by_customer(customer_email)
        if detail is None:
            return None
        if nickname is not None:
            detail.nickname = nickname
        if phone_number is not None:
            detail.phone_number = phone_number
        await self.session.flush()
        return detail
