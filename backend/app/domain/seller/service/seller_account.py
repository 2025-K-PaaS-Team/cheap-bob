from typing import Optional
from sqlalchemy.exc import IntegrityError

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
    async def find_or_create(self, email: str) -> Seller:
        """email 에 대응하는 seller row 를 멱등하게 보장한다.

        동시에 같은 신규 email 로 OAuth 콜백 두 개가 들어와도 안전 — 한쪽은 정상 INSERT,
        다른 쪽은 PK 충돌(IntegrityError) 을 catch 한 뒤 재조회로 winner row 를 돌려준다.
        """
        repo = SellerRepository(self._session)
        existing = await repo.find_by_email(email)
        if existing is not None:
            return existing
        try:
            return await repo.save(Seller(email=email))
        except IntegrityError:
            await self._session.rollback()
            existing = await repo.find_by_email(email)
            if existing is None:
                raise
            return existing


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
