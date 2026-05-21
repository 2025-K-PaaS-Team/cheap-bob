"""Tests for ``app.domain.customer.service.customer_preference.CustomerPreferenceService``.

4종 (menu / nutrition / allergy / topping) 이 동일 패턴이라 menu 1종을 대표 검증한 뒤
나머지 3종은 한 케이스씩만 회귀 확인한다.
"""
from types import SimpleNamespace
import pytest

from app.domain.seller.dto.nutrition import NutritionType
from app.domain.customer.dto.preference import (
    AllergyType,
    PreferredMenu,
    ToppingType,
)
from app.domain.customer.service.exception import (
    PreferenceDuplicateError,
    PreferenceNotFoundError,
)


# ───────── PreferredMenu (대표 검증) ─────────

@pytest.mark.unit
class TestPreferredMenu:

    async def test_list_returns_repo_result(self, service, menu_repo_mock):
        menu_repo_mock.find_by_customer.return_value = ["A"]
        result = await service.list_preferred_menus("alice@example.com")
        assert result == ["A"]


    async def test_add_returns_existing_plus_created(self, service, menu_repo_mock):
        menu_repo_mock.find_by_customer.return_value = [
            SimpleNamespace(menu_type=PreferredMenu.salad),
        ]

        result = await service.add_preferred_menus(
            "alice@example.com", [PreferredMenu.korean],
        )
        # save_bulk side_effect echo → [Enum.korean]
        assert len(result) == 2


    async def test_add_duplicate_raises(self, service, menu_repo_mock):
        menu_repo_mock.find_by_customer.return_value = [
            SimpleNamespace(menu_type=PreferredMenu.salad),
        ]
        with pytest.raises(PreferenceDuplicateError) as exc:
            await service.add_preferred_menus(
                "alice@example.com",
                [PreferredMenu.salad, PreferredMenu.korean],
            )
        assert "salad" in exc.value.duplicates


    async def test_remove_returns_when_deleted(self, service, menu_repo_mock):
        menu_repo_mock.delete.return_value = True
        # 정상 종료.
        await service.remove_preferred_menu(
            "alice@example.com", PreferredMenu.korean,
        )
        menu_repo_mock.delete.assert_awaited_once_with(
            "alice@example.com", PreferredMenu.korean,
        )


    async def test_remove_missing_raises(self, service, menu_repo_mock):
        menu_repo_mock.delete.return_value = False
        with pytest.raises(PreferenceNotFoundError):
            await service.remove_preferred_menu(
                "alice@example.com", PreferredMenu.korean,
            )


# ───────── 나머지 3종은 add/remove 한 케이스씩 (회귀 방지) ─────────

@pytest.mark.unit
class TestNutritionType:

    async def test_add(self, service, nutrition_repo_mock):
        nutrition_repo_mock.find_by_customer.return_value = []
        result = await service.add_nutrition_types(
            "alice@example.com", [NutritionType.diet],
        )
        assert len(result) == 1


    async def test_remove_missing_raises(self, service, nutrition_repo_mock):
        nutrition_repo_mock.delete.return_value = False
        with pytest.raises(PreferenceNotFoundError):
            await service.remove_nutrition_type(
                "alice@example.com", NutritionType.diet,
            )


@pytest.mark.unit
class TestAllergy:

    async def test_add(self, service, allergy_repo_mock):
        allergy_repo_mock.find_by_customer.return_value = []
        result = await service.add_allergies(
            "alice@example.com", [AllergyType.peanut],
        )
        assert len(result) == 1


@pytest.mark.unit
class TestToppingType:

    async def test_add_duplicate_raises(self, service, topping_repo_mock):
        topping_repo_mock.find_by_customer.return_value = [
            SimpleNamespace(topping_type=ToppingType.avocado),
        ]
        with pytest.raises(PreferenceDuplicateError):
            await service.add_topping_types(
                "alice@example.com", [ToppingType.avocado],
            )
