from typing import Optional
from sqlalchemy.exc import IntegrityError

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
    async def find_or_create(self, email: str) -> Customer:
        """email 에 대응하는 customer row 를 멱등하게 보장한다.

        동시에 같은 신규 email 로 OAuth 콜백 두 개가 들어와도 안전 — 한쪽은 정상 INSERT,
        다른 쪽은 PK 충돌(IntegrityError) 을 catch 한 뒤 재조회로 winner row 를 돌려준다.
        OAuth 외 호출자(예: 관리 도구의 신규 가입) 도 같은 보장으로 묶을 수 있다.
        """
        repo = CustomerRepository(self._session)
        existing = await repo.find_by_email(email)
        if existing is not None:
            return existing
        try:
            return await repo.save(Customer(email=email))
        except IntegrityError:
            # 다른 tx 가 먼저 INSERT 했다. session 을 깨끗하게 만들고 재조회.
            await self._session.rollback()
            existing = await repo.find_by_email(email)
            if existing is None:
                # IntegrityError 가 났는데 재조회 시 사라졌다면 진짜 비정상 — 그대로 raise.
                raise
            return existing


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
