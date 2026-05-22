"""CustomerProfileService 의 실 DB 흐름.

비즈니스 시나리오:
  1) ``get_full_profile`` 은 detail + 4종 선호를 eager-load 한 Customer 반환
  2) detail 이 없으면 ``CustomerDetailNotFoundError``
  3) ``get_preference_snapshot`` 은 comma-joined 문자열로 customer 4종 선호를 패키징
  4) customer 자체가 없으면 snapshot 의 모든 값이 None
"""
import pytest_asyncio
import pytest

from app.domain.seller.dto.nutrition import NutritionType
from app.domain.customer.service.exception import CustomerDetailNotFoundError
from app.domain.customer.service.customer_profile import CustomerProfileService
from app.domain.customer.dto.preference import (
    AllergyType,
    PreferredMenu,
    ToppingType,
)


pytestmark = pytest.mark.integration


@pytest_asyncio.fixture
def customer_profile_service(uow):
    return CustomerProfileService(uow=uow)


@pytest_asyncio.fixture
async def seed_customer_with_preferences(seed_customer, session_factory):
    """customer + detail + 4종 선호를 한 세트 심는다."""
    from app.domain.customer.model.customer_allergy import CustomerAllergy
    from app.domain.customer.model.customer_nutrition_type import CustomerNutritionType
    from app.domain.customer.model.customer_preferred_menu import CustomerPreferredMenu
    from app.domain.customer.model.customer_topping_type import CustomerToppingType

    async def _seed() -> str:
        [email] = await seed_customer(1)
        async with session_factory() as session:
            session.add(CustomerPreferredMenu(
                customer_email=email, menu_type=PreferredMenu.korean,
            ))
            session.add(CustomerNutritionType(
                customer_email=email, nutrition_type=NutritionType.protein,
            ))
            session.add(CustomerAllergy(
                customer_email=email, allergy_type=AllergyType.peanut,
            ))
            session.add(CustomerToppingType(
                customer_email=email, topping_type=ToppingType.avocado,
            ))
            await session.commit()
        return email

    return _seed


class TestGetFullProfile:

    async def test_returns_customer_with_relations(
        self, customer_profile_service, seed_customer_with_preferences,
    ):
        email = await seed_customer_with_preferences()

        customer = await customer_profile_service.get_full_profile(email)
        assert customer.email == email
        assert customer.detail is not None
        assert len(customer.preferred_menus) == 1
        assert len(customer.nutrition_types) == 1
        assert len(customer.allergies) == 1
        assert len(customer.topping_types) == 1


    async def test_raises_when_detail_missing(
        self, customer_profile_service, session_factory,
    ):
        from app.domain.customer.model.customer import Customer
        async with session_factory() as session:
            session.add(Customer(email="bare@example.com", is_active=True))
            await session.commit()

        with pytest.raises(CustomerDetailNotFoundError):
            await customer_profile_service.get_full_profile("bare@example.com")


class TestGetPreferenceSnapshot:

    async def test_joins_enum_values_with_comma(
        self, customer_profile_service, seed_customer_with_preferences,
    ):
        email = await seed_customer_with_preferences()

        snap = await customer_profile_service.get_preference_snapshot(email)
        assert snap["preferred_menus"] == "korean"
        assert snap["nutrition_types"] == "protein"
        assert snap["allergies"] == "peanut"
        assert snap["topping_types"] == "avocado"


    async def test_all_none_when_customer_missing(self, customer_profile_service):
        snap = await customer_profile_service.get_preference_snapshot(
            "ghost@example.com",
        )
        assert snap == {
            "preferred_menus": None,
            "nutrition_types": None,
            "allergies": None,
            "topping_types": None,
        }
