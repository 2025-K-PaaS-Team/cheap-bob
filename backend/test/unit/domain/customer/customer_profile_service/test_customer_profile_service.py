"""Tests for ``app.domain.customer.service.customer_profile.CustomerProfileService``."""
from types import SimpleNamespace
import pytest

from app.domain.customer.dto.preference import (
    AllergyType,
    NutritionType,
    PreferredMenu,
    ToppingType,
)
from app.domain.customer.service.exception import CustomerDetailNotFoundError


@pytest.mark.unit
class TestGetFullProfile:

    async def test_raises_when_customer_missing(self, service, profile_repo_mock):
        profile_repo_mock.find_full_profile.return_value = None
        with pytest.raises(CustomerDetailNotFoundError):
            await service.get_full_profile("alice@example.com")


    async def test_raises_when_detail_missing(self, service, profile_repo_mock):
        # Customer 는 있는데 detail 만 None.
        profile_repo_mock.find_full_profile.return_value = SimpleNamespace(detail=None)
        with pytest.raises(CustomerDetailNotFoundError):
            await service.get_full_profile("alice@example.com")


    async def test_returns_customer(self, service, profile_repo_mock):
        customer = SimpleNamespace(detail=SimpleNamespace(nickname="닉"))
        profile_repo_mock.find_full_profile.return_value = customer

        result = await service.get_full_profile("alice@example.com")
        assert result is customer


@pytest.mark.unit
class TestGetPreferenceSnapshot:

    async def test_all_none_when_customer_missing(self, service, profile_repo_mock):
        profile_repo_mock.find_full_profile.return_value = None
        snap = await service.get_preference_snapshot("ghost@example.com")
        assert snap == {
            "preferred_menus": None,
            "nutrition_types": None,
            "allergies": None,
            "topping_types": None,
        }


    async def test_joins_enum_values_with_comma(self, service, profile_repo_mock):
        customer = SimpleNamespace(
            preferred_menus=[
                SimpleNamespace(menu_type=PreferredMenu.korean),
                SimpleNamespace(menu_type=PreferredMenu.salad),
            ],
            nutrition_types=[SimpleNamespace(nutrition_type=NutritionType.protein)],
            allergies=[SimpleNamespace(allergy_type=AllergyType.peanut)],
            topping_types=[SimpleNamespace(topping_type=ToppingType.avocado)],
        )
        profile_repo_mock.find_full_profile.return_value = customer

        snap = await service.get_preference_snapshot("alice@example.com")
        assert snap["preferred_menus"] == "korean,salad"
        assert snap["nutrition_types"] == "protein"
        assert snap["allergies"] == "peanut"
        assert snap["topping_types"] == "avocado"


    async def test_empty_lists_return_none(self, service, profile_repo_mock):
        """customer 가 있지만 4종이 모두 빈 리스트면 join_values 가 None 을 돌려준다."""
        customer = SimpleNamespace(
            preferred_menus=[], nutrition_types=[], allergies=[], topping_types=[],
        )
        profile_repo_mock.find_full_profile.return_value = customer

        snap = await service.get_preference_snapshot("alice@example.com")
        assert snap == {
            "preferred_menus": None,
            "nutrition_types": None,
            "allergies": None,
            "topping_types": None,
        }
