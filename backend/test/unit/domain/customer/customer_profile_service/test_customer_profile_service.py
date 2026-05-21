"""Tests for ``app.domain.customer.service.customer_profile.CustomerProfileService``."""
from types import SimpleNamespace
import pytest

from app.domain.customer.service.exception import CustomerDetailNotFoundError
from app.domain.customer.dto.profile import CustomerFullProfile
from app.domain.seller.dto.nutrition import NutritionType
from app.domain.customer.dto.preference import (
    AllergyType,
    PreferredMenu,
    ToppingType,
)


@pytest.mark.unit
class TestGetFullProfile:

    async def test_raises_when_detail_missing(self, service, profile_repos):
        profile_repos.detail.find_by_customer.return_value = None
        with pytest.raises(CustomerDetailNotFoundError):
            await service.get_full_profile("alice@example.com")


    async def test_returns_full_profile_dto(self, service, profile_repos):
        detail = SimpleNamespace(nickname="닉")
        menus = [SimpleNamespace(menu_type=PreferredMenu.salad)]
        nutritions = [SimpleNamespace(nutrition_type=NutritionType.protein)]
        allergies = [SimpleNamespace(allergy_type=AllergyType.peanut)]
        toppings = [SimpleNamespace(topping_type=ToppingType.avocado)]
        profile_repos.detail.find_by_customer.return_value = detail
        profile_repos.preferred_menus.find_by_customer.return_value = menus
        profile_repos.nutrition_types.find_by_customer.return_value = nutritions
        profile_repos.allergies.find_by_customer.return_value = allergies
        profile_repos.topping_types.find_by_customer.return_value = toppings

        result = await service.get_full_profile("alice@example.com")
        assert isinstance(result, CustomerFullProfile)
        assert result.detail is detail
        assert result.preferred_menus is menus
        assert result.nutrition_types is nutritions
        assert result.allergies is allergies
        assert result.topping_types is toppings


@pytest.mark.unit
class TestGetPreferenceSnapshot:

    async def test_all_none_when_no_preferences(self, service, profile_repos):
        # 자식 repo 4개가 모두 빈 리스트 → 전부 None.
        snap = await service.get_preference_snapshot("ghost@example.com")
        assert snap == {
            "preferred_menus": None,
            "nutrition_types": None,
            "allergies": None,
            "topping_types": None,
        }


    async def test_joins_enum_values_with_comma(self, service, profile_repos):
        profile_repos.preferred_menus.find_by_customer.return_value = [
            SimpleNamespace(menu_type=PreferredMenu.korean),
            SimpleNamespace(menu_type=PreferredMenu.salad),
        ]
        profile_repos.nutrition_types.find_by_customer.return_value = [
            SimpleNamespace(nutrition_type=NutritionType.protein),
        ]
        profile_repos.allergies.find_by_customer.return_value = [
            SimpleNamespace(allergy_type=AllergyType.peanut),
        ]
        profile_repos.topping_types.find_by_customer.return_value = [
            SimpleNamespace(topping_type=ToppingType.avocado),
        ]

        snap = await service.get_preference_snapshot("alice@example.com")
        assert snap["preferred_menus"] == "korean,salad"
        assert snap["nutrition_types"] == "protein"
        assert snap["allergies"] == "peanut"
        assert snap["topping_types"] == "avocado"
