from typing import Optional

from app.domain.customer.service.exception import CustomerNotFoundError
from app.domain.customer.repository.customer import CustomerRepository
from app.domain.customer.model.customer import Customer
from app.database.session import UnitOfWork, transactional


class CustomerAccountService:
    """소비자 계정 (customers row) 의 CRUD + 활성 토글.

    auth 도메인의 OAuth 흐름이 본 서비스를 호출해 1차 가입 / 조회를 수행한다.
    customer 탈퇴 흐름은 is_active 토글 + hard_delete 를 호출한다.
    """

    def __init__(self, uow: UnitOfWork):
        self.uow = uow


    @transactional
    async def find_by_email(self, email: str) -> Optional[Customer]:
        return await CustomerRepository(self._session).find_by_email(email)


    @transactional
    async def create(self, email: str) -> Customer:
        """신규 customer row 생성. is_active=True 로 시작."""
        return await CustomerRepository(self._session).save(Customer(email=email))


    @transactional
    async def is_active(self, email: str) -> bool:
        customer = await CustomerRepository(self._session).find_by_email(email)
        if customer is None:
            raise CustomerNotFoundError("소비자를 찾을 수 없습니다")
        return customer.is_active


    @transactional
    async def set_active(self, email: str, *, active: bool) -> None:
        customer = await CustomerRepository(self._session).find_by_email(email)
        if customer is None:
            raise CustomerNotFoundError("소비자를 찾을 수 없습니다")
        customer.is_active = active
        await self._session.flush()


    @transactional
    async def hard_delete(self, email: str) -> bool:
        """탈퇴 cleanup worker 가 호출. cascade 삭제로 관련 정보까지 한 번에 제거."""
        return await CustomerRepository(self._session).delete_by_email(email)
