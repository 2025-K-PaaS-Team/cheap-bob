"""SellerAccountService 의 실 DB 흐름.

비즈니스 시나리오:
  1) seed 한 seller 의 is_active 토글이 DB 에 반영된다
  2) 존재하지 않는 이메일이면 SellerNotFoundError
  3) hard_delete 가 seller 를 비운다
  4) hard_delete 의 반환값이 대상 부재 시 False
"""
import pytest
import pytest_asyncio

from app.domain.seller.service.seller_account import SellerAccountService
from app.domain.seller.service.exception import SellerNotFoundError


pytestmark = pytest.mark.integration


@pytest_asyncio.fixture
def seller_account_service(uow):
    return SellerAccountService(uow=uow)


class TestSetActive:

    async def test_toggles_is_active(
        self, seller_account_service, seed_seller, session_factory,
    ):
        [email] = await seed_seller(1)

        await seller_account_service.set_active(email, active=False)

        from app.domain.seller.model.seller import Seller
        async with session_factory() as session:
            seller = await session.get(Seller, email)
            assert seller.is_active is False


    async def test_missing_seller_raises(self, seller_account_service):
        with pytest.raises(SellerNotFoundError):
            await seller_account_service.set_active(
                "ghost@example.com", active=True,
            )


class TestIsActive:

    async def test_reflects_db_state(
        self, seller_account_service, seed_seller,
    ):
        [email] = await seed_seller(1)
        assert await seller_account_service.is_active(email) is True

        await seller_account_service.set_active(email, active=False)
        assert await seller_account_service.is_active(email) is False


    async def test_missing_raises(self, seller_account_service):
        with pytest.raises(SellerNotFoundError):
            await seller_account_service.is_active("ghost@example.com")


class TestHardDelete:

    async def test_removes_seller(
        self, seller_account_service, seed_seller, session_factory,
    ):
        [email] = await seed_seller(1)

        deleted = await seller_account_service.hard_delete(email)
        assert deleted is True

        from app.domain.seller.model.seller import Seller
        async with session_factory() as session:
            assert await session.get(Seller, email) is None


    async def test_returns_false_when_missing(self, seller_account_service):
        assert (
            await seller_account_service.hard_delete("ghost@example.com")
            is False
        )
