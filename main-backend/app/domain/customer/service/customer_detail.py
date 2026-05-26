from typing import Optional

from app.domain.customer.service.exception import CustomerDetailNotFoundError
from app.domain.customer.repository.customer_detail import CustomerDetailRepository
from app.domain.customer.model.customer_detail import CustomerDetail
from app.database.session import UnitOfWork, transactional


class CustomerDetailService:
    """소비자 상세 정보의 GET / PATCH 비즈니스 로직."""

    def __init__(self, uow: UnitOfWork):
        self.uow = uow


    @transactional
    async def get(self, customer_email: str) -> CustomerDetail:
        detail = await CustomerDetailRepository(self._session).find_by_customer(
            customer_email,
        )
        if detail is None:
            raise CustomerDetailNotFoundError("소비자 상세 정보가 등록되지 않았습니다")
        return detail


    @transactional
    async def update(
        self,
        *,
        customer_email: str,
        nickname: Optional[str],
        phone_number: Optional[str],
    ) -> CustomerDetail:
        repo = CustomerDetailRepository(self._session)
        detail = await repo.update(
            customer_email,
            nickname=nickname,
            phone_number=phone_number,
        )
        if detail is None:
            raise CustomerDetailNotFoundError("소비자 상세 정보가 등록되지 않았습니다")
        return detail
