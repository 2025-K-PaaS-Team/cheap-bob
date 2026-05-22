"""CustomerAccountService 의 실 DB 흐름.

비즈니스 시나리오:
  1) seed 한 customer 의 is_active 토글이 DB 에 반영된다
  2) 존재하지 않는 이메일이면 CustomerNotFoundError
  3) hard_delete 가 customer 의 cascade (detail / preference / favorite) 를 모두 비운다
  4) hard_delete 의 반환값이 대상 부재 시 False
"""
import pytest_asyncio
import pytest

from app.domain.customer.service.exception import CustomerNotFoundError
from app.domain.customer.service.customer_account import CustomerAccountService


pytestmark = pytest.mark.integration


@pytest_asyncio.fixture
def customer_account_service(uow):
    return CustomerAccountService(uow=uow)


class TestSetActive:

    async def test_toggles_is_active(
        self, customer_account_service, seed_customer, session_factory,
    ):
        [email] = await seed_customer(1)

        await customer_account_service.set_active(email, active=False)

        from app.domain.customer.model.customer import Customer
        async with session_factory() as session:
            customer = await session.get(Customer, email)
            assert customer.is_active is False


    async def test_missing_customer_raises(self, customer_account_service):
        with pytest.raises(CustomerNotFoundError):
            await customer_account_service.set_active(
                "ghost@example.com", active=True,
            )


class TestIsActive:

    async def test_reflects_db_state(
        self, customer_account_service, seed_customer,
    ):
        [email] = await seed_customer(1)
        assert await customer_account_service.is_active(email) is True

        await customer_account_service.set_active(email, active=False)
        assert await customer_account_service.is_active(email) is False


    async def test_missing_raises(self, customer_account_service):
        with pytest.raises(CustomerNotFoundError):
            await customer_account_service.is_active("ghost@example.com")


class TestHardDelete:

    async def test_cascades_detail(
        self, customer_account_service, seed_customer, session_factory,
    ):
        # seed_customer 는 Customer + CustomerDetail 한 세트를 심으므로 cascade 확인용으로 충분.
        [email] = await seed_customer(1)

        deleted = await customer_account_service.hard_delete(email)
        assert deleted is True

        from app.domain.customer.model.customer import Customer
        from app.domain.customer.model.customer_detail import CustomerDetail
        async with session_factory() as session:
            assert await session.get(Customer, email) is None
            assert await session.get(CustomerDetail, email) is None


    async def test_returns_false_when_missing(self, customer_account_service):
        assert (
            await customer_account_service.hard_delete("ghost@example.com")
            is False
        )
