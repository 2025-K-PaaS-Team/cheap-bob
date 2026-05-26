"""CustomerPreferenceService 의 실 DB 흐름.

비즈니스 시나리오:
  1) 4종 선호의 list / add / remove 가 각각 같은 패턴으로 동작
  2) ``add_*`` 는 기존 항목 + 신규 추가 합본을 반환 (overlap 시 ``PreferenceDuplicateError``)
  3) ``remove_*`` 는 대상 미존재 시 ``PreferenceNotFoundError``

(4종 중 PreferredMenu / Allergy 두 가지만 검증해도 동일 패턴 확인에 충분하지만,
나머지 두 종류도 회귀 방지를 위해 동일하게 한 케이스씩 검사한다.)
"""
import pytest_asyncio
import pytest

from app.domain.seller.dto.nutrition import NutritionType
from app.domain.customer.service.exception import (
    PreferenceDuplicateError,
    PreferenceNotFoundError,
)
from app.domain.customer.service.customer_preference import CustomerPreferenceService
from app.domain.customer.dto.preference import (
    AllergyType,
    PreferredMenu,
    ToppingType,
)


pytestmark = pytest.mark.integration


@pytest_asyncio.fixture
def customer_preference_service(uow):
    return CustomerPreferenceService(uow=uow)


class TestPreferredMenu:

    async def test_add_and_list(
        self, customer_preference_service, seed_customer,
    ):
        [email] = await seed_customer(1)

        result = await customer_preference_service.add_preferred_menus(
            email, [PreferredMenu.salad, PreferredMenu.korean],
        )
        assert {m.menu_type for m in result} == {
            PreferredMenu.salad, PreferredMenu.korean,
        }

        listed = await customer_preference_service.list_preferred_menus(email)
        assert {m.menu_type for m in listed} == {
            PreferredMenu.salad, PreferredMenu.korean,
        }


    async def test_duplicate_add_raises(
        self, customer_preference_service, seed_customer,
    ):
        [email] = await seed_customer(1)
        await customer_preference_service.add_preferred_menus(
            email, [PreferredMenu.salad],
        )

        with pytest.raises(PreferenceDuplicateError):
            await customer_preference_service.add_preferred_menus(
                email, [PreferredMenu.salad, PreferredMenu.korean],
            )


    async def test_remove(
        self, customer_preference_service, seed_customer,
    ):
        [email] = await seed_customer(1)
        await customer_preference_service.add_preferred_menus(
            email, [PreferredMenu.korean],
        )

        await customer_preference_service.remove_preferred_menu(
            email, PreferredMenu.korean,
        )
        assert await customer_preference_service.list_preferred_menus(email) == []


    async def test_remove_missing_raises(
        self, customer_preference_service, seed_customer,
    ):
        [email] = await seed_customer(1)
        with pytest.raises(PreferenceNotFoundError):
            await customer_preference_service.remove_preferred_menu(
                email, PreferredMenu.korean,
            )


class TestNutritionType:

    async def test_add_and_remove_round_trip(
        self, customer_preference_service, seed_customer,
    ):
        [email] = await seed_customer(1)
        added = await customer_preference_service.add_nutrition_types(
            email, [NutritionType.diet],
        )
        assert added[0].nutrition_type == NutritionType.diet

        await customer_preference_service.remove_nutrition_type(
            email, NutritionType.diet,
        )
        assert await customer_preference_service.list_nutrition_types(email) == []


class TestAllergy:

    async def test_add_and_remove_round_trip(
        self, customer_preference_service, seed_customer,
    ):
        [email] = await seed_customer(1)
        await customer_preference_service.add_allergies(
            email, [AllergyType.peanut, AllergyType.egg],
        )

        await customer_preference_service.remove_allergy(email, AllergyType.peanut)
        listed = await customer_preference_service.list_allergies(email)
        assert {a.allergy_type for a in listed} == {AllergyType.egg}


class TestToppingType:

    async def test_add_and_remove_round_trip(
        self, customer_preference_service, seed_customer,
    ):
        [email] = await seed_customer(1)
        await customer_preference_service.add_topping_types(
            email, [ToppingType.avocado, ToppingType.shrimp],
        )

        await customer_preference_service.remove_topping_type(
            email, ToppingType.avocado,
        )
        listed = await customer_preference_service.list_topping_types(email)
        assert {t.topping_type for t in listed} == {ToppingType.shrimp}
