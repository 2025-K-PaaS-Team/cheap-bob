"""CustomerRegisterService 의 실 DB 흐름.

비즈니스 시나리오:
  1) detail + 4종 선호를 한 트랜잭션으로 등록
  2) 이미 detail 이 있는 customer 의 재등록 시도는 ``CustomerAlreadyRegisteredError``
  3) 선호도 인자가 None 인 항목은 row 가 생기지 않는다
"""
import pytest
import pytest_asyncio

from app.domain.seller.dto.nutrition import NutritionType
from app.domain.customer.dto.preference import (
    AllergyType,
    PreferredMenu,
    ToppingType,
)
from app.domain.customer.service.customer_register import CustomerRegisterService
from app.domain.customer.service.exception import CustomerAlreadyRegisteredError


pytestmark = pytest.mark.integration


@pytest_asyncio.fixture
def customer_register_service(uow):
    return CustomerRegisterService(uow=uow)


@pytest_asyncio.fixture
async def seed_bare_customer(session_factory):
    """detail 없는 Customer 만 만든다 (1차 OAuth 가입 직후 상태)."""
    from app.domain.customer.model.customer import Customer

    counter = {"value": 0}

    async def _seed() -> str:
        async with session_factory() as session:
            idx = counter["value"]
            counter["value"] += 1
            email = f"bare_it_{idx:03d}@example.com"
            session.add(Customer(email=email, is_active=True))
            await session.commit()
        return email

    return _seed


class TestRegister:

    async def test_persists_detail_and_all_preferences(
        self, customer_register_service, seed_bare_customer, session_factory,
    ):
        email = await seed_bare_customer()

        detail, menus, nutritions, allergies, toppings = (
            await customer_register_service.register(
                customer_email=email,
                nickname="홍길동",
                phone_number="01012345678",
                preferred_menus=[PreferredMenu.salad, PreferredMenu.korean],
                nutrition_types=[NutritionType.protein],
                allergies=[AllergyType.peanut, AllergyType.dairy],
                topping_types=[ToppingType.avocado],
            )
        )

        assert detail.nickname == "홍길동"
        assert detail.phone_number == "01012345678"
        assert len(menus) == 2
        assert len(nutritions) == 1
        assert len(allergies) == 2
        assert len(toppings) == 1

        # DB 에 실제로 들어가 있는지 직접 확인.
        from app.domain.customer.model.customer_detail import CustomerDetail
        from app.domain.customer.model.customer_preferred_menu import (
            CustomerPreferredMenu,
        )
        from sqlalchemy import select
        async with session_factory() as session:
            assert await session.get(CustomerDetail, email) is not None
            result = await session.execute(
                select(CustomerPreferredMenu).where(
                    CustomerPreferredMenu.customer_email == email,
                ),
            )
            assert len(result.scalars().all()) == 2


    async def test_omitted_preferences_create_no_rows(
        self, customer_register_service, seed_bare_customer, session_factory,
    ):
        email = await seed_bare_customer()

        await customer_register_service.register(
            customer_email=email,
            nickname="민수",
            phone_number="01099998888",
            preferred_menus=None,
            nutrition_types=None,
            allergies=None,
            topping_types=None,
        )

        from app.domain.customer.model.customer_preferred_menu import (
            CustomerPreferredMenu,
        )
        from sqlalchemy import select
        async with session_factory() as session:
            result = await session.execute(
                select(CustomerPreferredMenu).where(
                    CustomerPreferredMenu.customer_email == email,
                ),
            )
            assert result.scalars().all() == []


    async def test_register_twice_raises(
        self, customer_register_service, seed_bare_customer,
    ):
        email = await seed_bare_customer()

        await customer_register_service.register(
            customer_email=email,
            nickname="aaaa",
            phone_number="01000000000",
            preferred_menus=None,
            nutrition_types=None,
            allergies=None,
            topping_types=None,
        )

        with pytest.raises(CustomerAlreadyRegisteredError):
            await customer_register_service.register(
                customer_email=email,
                nickname="bbbb",
                phone_number="01011112222",
                preferred_menus=None,
                nutrition_types=None,
                allergies=None,
                topping_types=None,
            )
