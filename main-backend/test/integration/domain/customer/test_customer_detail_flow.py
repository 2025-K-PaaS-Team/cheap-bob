"""CustomerDetailService 의 실 DB 흐름.

비즈니스 시나리오:
  1) seed 한 customer 의 detail 을 조회 가능
  2) 미등록 시 ``CustomerDetailNotFoundError``
  3) ``update`` 는 None 이 아닌 필드만 갱신 (partial patch)
  4) 미등록 customer 에 대한 update 는 ``CustomerDetailNotFoundError``
"""
import pytest_asyncio
import pytest

from app.domain.customer.service.exception import CustomerDetailNotFoundError
from app.domain.customer.service.customer_detail import CustomerDetailService


pytestmark = pytest.mark.integration


@pytest_asyncio.fixture
def customer_detail_service(uow):
    return CustomerDetailService(uow=uow)


class TestGet:

    async def test_returns_detail_for_seeded_customer(
        self, customer_detail_service, seed_customer,
    ):
        [email] = await seed_customer(1)

        detail = await customer_detail_service.get(email)
        assert detail.customer_email == email
        # seed_customer 의 닉네임/전화번호 규칙 (conftest 참고).
        assert detail.nickname.startswith("닉네임")
        assert detail.phone_number.startswith("010")
        assert len(detail.phone_number) == 11


    async def test_raises_when_detail_missing(
        self, customer_detail_service, session_factory,
    ):
        # detail 없이 Customer 만 심는다.
        from app.domain.customer.model.customer import Customer
        async with session_factory() as session:
            session.add(Customer(email="bare@example.com", is_active=True))
            await session.commit()

        with pytest.raises(CustomerDetailNotFoundError):
            await customer_detail_service.get("bare@example.com")


class TestUpdate:

    async def test_partial_update_only_changes_provided_fields(
        self, customer_detail_service, seed_customer,
    ):
        [email] = await seed_customer(1)
        before = await customer_detail_service.get(email)
        original_phone = before.phone_number

        updated = await customer_detail_service.update(
            customer_email=email, nickname="새닉", phone_number=None,
        )

        assert updated.nickname == "새닉"
        assert updated.phone_number == original_phone


    async def test_raises_when_customer_missing(self, customer_detail_service):
        with pytest.raises(CustomerDetailNotFoundError):
            await customer_detail_service.update(
                customer_email="ghost@example.com",
                nickname="x",
                phone_number=None,
            )
