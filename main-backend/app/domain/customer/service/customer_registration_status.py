from app.domain.customer.repository.customer_detail import CustomerDetailRepository
from app.database.session import UnitOfWork, transactional


class CustomerRegistrationStatusService:
    """소비자의 온보딩 진행 상태 ("profile" | "complete").

    auth 도메인의 `RegistrationStatusService` 가 customer 분기에서 본 서비스를 호출한다.
    seller 분기는 seller 도메인 분리 시 동일 패턴으로 따로 둔다.
    """

    def __init__(self, uow: UnitOfWork):
        self.uow = uow


    @transactional
    async def get_status(self, customer_email: str) -> str:
        repo = CustomerDetailRepository(self._session)
        return "complete" if await repo.exists_by_customer(customer_email) else "profile"
