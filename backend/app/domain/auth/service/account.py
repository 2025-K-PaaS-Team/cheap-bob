"""auth 계정 활성/비활성 토글. customer/seller withdraw 가 호출하는 진입점."""
from app.domain.auth.service.exception import CustomerNotFoundError, SellerNotFoundError
from app.domain.auth.repository.seller import SellerRepository
from app.domain.auth.repository.customer import CustomerRepository
from app.database.session import UnitOfWork, transactional


class AuthAccountService:

    def __init__(self, uow: UnitOfWork):
        self.uow = uow


    @transactional
    async def set_customer_active(self, customer_email: str, *, active: bool) -> None:
        customer = await CustomerRepository(self._session).find_by_email(customer_email)
        if customer is None:
            raise CustomerNotFoundError("소비자를 찾을 수 없습니다")
        customer.is_active = active
        await self._session.flush()


    @transactional
    async def set_seller_active(self, seller_email: str, *, active: bool) -> None:
        seller = await SellerRepository(self._session).find_by_email(seller_email)
        if seller is None:
            raise SellerNotFoundError("판매자를 찾을 수 없습니다")
        seller.is_active = active
        await self._session.flush()


    @transactional
    async def is_customer_active(self, customer_email: str) -> bool:
        customer = await CustomerRepository(self._session).find_by_email(customer_email)
        if customer is None:
            raise CustomerNotFoundError("소비자를 찾을 수 없습니다")
        return customer.is_active


    @transactional
    async def is_seller_active(self, seller_email: str) -> bool:
        seller = await SellerRepository(self._session).find_by_email(seller_email)
        if seller is None:
            raise SellerNotFoundError("판매자를 찾을 수 없습니다")
        return seller.is_active


    @transactional
    async def hard_delete_customer(self, email: str) -> bool:
        """탈퇴 cleanup worker 가 호출. cascade 삭제로 관련 정보까지 한 번에 제거."""
        return await CustomerRepository(self._session).delete_by_email(email)


    @transactional
    async def hard_delete_seller(self, email: str) -> bool:
        """탈퇴 cleanup worker 가 호출."""
        return await SellerRepository(self._session).delete_by_email(email)
