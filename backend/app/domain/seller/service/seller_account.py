from typing import Optional

from app.domain.seller.service.exception import SellerNotFoundError
from app.domain.seller.repository.seller import SellerRepository
from app.domain.seller.model.seller import Seller
from app.database.session import UnitOfWork, transactional


class SellerAccountService:
    """판매자 계정 (sellers row) 의 CRUD + 활성 토글.

    auth 도메인의 OAuth 흐름이 본 서비스를 호출해 1차 가입 / 조회를 수행한다.
    seller 탈퇴 흐름은 is_active 토글 + hard_delete 를 호출한다.
    """

    def __init__(self, uow: UnitOfWork):
        self.uow = uow


    @transactional
    async def find_by_email(self, email: str) -> Optional[Seller]:
        return await SellerRepository(self._session).find_by_email(email)


    @transactional
    async def create(self, email: str) -> Seller:
        """신규 seller row 생성. is_active=True 로 시작."""
        return await SellerRepository(self._session).save(Seller(email=email))


    @transactional
    async def is_active(self, email: str) -> bool:
        seller = await SellerRepository(self._session).find_by_email(email)
        if seller is None:
            raise SellerNotFoundError("판매자를 찾을 수 없습니다")
        return seller.is_active


    @transactional
    async def set_active(self, email: str, *, active: bool) -> None:
        seller = await SellerRepository(self._session).find_by_email(email)
        if seller is None:
            raise SellerNotFoundError("판매자를 찾을 수 없습니다")
        seller.is_active = active
        await self._session.flush()


    @transactional
    async def hard_delete(self, email: str) -> bool:
        """탈퇴 cleanup worker 가 호출."""
        return await SellerRepository(self._session).delete_by_email(email)
