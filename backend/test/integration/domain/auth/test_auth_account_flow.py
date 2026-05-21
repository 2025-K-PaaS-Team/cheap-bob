"""AuthAccountService 의 실 DB 흐름.

비즈니스 시나리오:
  1) seed 한 customer/seller 의 is_active 토글이 DB 에 반영된다
  2) 존재하지 않는 이메일이면 도메인별 NotFound 예외
  3) hard_delete 가 customer 의 cascade (detail / preference / favorite) 를 모두 비운다
  4) hard_delete 의 반환값이 대상 부재 시 False
"""
import pytest
import pytest_asyncio

from app.domain.auth.service.account import AuthAccountService
from app.domain.auth.service.exception import (
    CustomerNotFoundError,
    SellerNotFoundError,
)


pytestmark = pytest.mark.integration


@pytest_asyncio.fixture
def auth_account_service(uow):
    return AuthAccountService(uow=uow)


class TestSetActive:

    async def test_toggles_customer_is_active(
        self, auth_account_service, seed_customer, session_factory,
    ):
        [email] = await seed_customer(1)

        await auth_account_service.set_customer_active(email, active=False)

        from app.domain.auth.model.customer import Customer
        async with session_factory() as session:
            customer = await session.get(Customer, email)
            assert customer.is_active is False


    async def test_toggles_seller_is_active(
        self, auth_account_service, seed_seller, session_factory,
    ):
        [email] = await seed_seller(1)

        await auth_account_service.set_seller_active(email, active=False)

        from app.domain.auth.model.seller import Seller
        async with session_factory() as session:
            seller = await session.get(Seller, email)
            assert seller.is_active is False


    async def test_missing_customer_raises(self, auth_account_service):
        with pytest.raises(CustomerNotFoundError):
            await auth_account_service.set_customer_active(
                "ghost@example.com", active=True,
            )


    async def test_missing_seller_raises(self, auth_account_service):
        with pytest.raises(SellerNotFoundError):
            await auth_account_service.set_seller_active(
                "ghost@example.com", active=True,
            )


class TestIsActive:

    async def test_reflects_db_state_for_customer(
        self, auth_account_service, seed_customer,
    ):
        [email] = await seed_customer(1)
        assert await auth_account_service.is_customer_active(email) is True

        await auth_account_service.set_customer_active(email, active=False)
        assert await auth_account_service.is_customer_active(email) is False


    async def test_reflects_db_state_for_seller(
        self, auth_account_service, seed_seller,
    ):
        [email] = await seed_seller(1)
        assert await auth_account_service.is_seller_active(email) is True

        await auth_account_service.set_seller_active(email, active=False)
        assert await auth_account_service.is_seller_active(email) is False


    async def test_missing_customer_raises(self, auth_account_service):
        with pytest.raises(CustomerNotFoundError):
            await auth_account_service.is_customer_active("ghost@example.com")


    async def test_missing_seller_raises(self, auth_account_service):
        with pytest.raises(SellerNotFoundError):
            await auth_account_service.is_seller_active("ghost@example.com")


class TestHardDelete:

    async def test_hard_delete_customer_cascades_detail(
        self, auth_account_service, seed_customer, session_factory,
    ):
        # seed_customer 는 Customer + CustomerDetail 한 세트를 심으므로 cascade 확인용으로 충분.
        [email] = await seed_customer(1)

        deleted = await auth_account_service.hard_delete_customer(email)
        assert deleted is True

        from app.domain.auth.model.customer import Customer
        from app.domain.customer.model.customer_detail import CustomerDetail
        async with session_factory() as session:
            assert await session.get(Customer, email) is None
            assert await session.get(CustomerDetail, email) is None


    async def test_hard_delete_customer_returns_false_when_missing(
        self, auth_account_service,
    ):
        assert (
            await auth_account_service.hard_delete_customer("ghost@example.com")
            is False
        )


    async def test_hard_delete_seller(
        self, auth_account_service, seed_seller, session_factory,
    ):
        [email] = await seed_seller(1)

        deleted = await auth_account_service.hard_delete_seller(email)
        assert deleted is True

        from app.domain.auth.model.seller import Seller
        async with session_factory() as session:
            assert await session.get(Seller, email) is None


    async def test_hard_delete_seller_returns_false_when_missing(
        self, auth_account_service,
    ):
        assert (
            await auth_account_service.hard_delete_seller("ghost@example.com")
            is False
        )
