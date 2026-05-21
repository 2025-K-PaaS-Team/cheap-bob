"""Tests for ``app.domain.customer.service.customer_register.CustomerRegisterService``."""
import pytest

from app.domain.seller.dto.nutrition import NutritionType
from app.domain.customer.dto.preference import (
    AllergyType,
    PreferredMenu,
    ToppingType,
)
from app.domain.customer.service.exception import CustomerAlreadyRegisteredError


@pytest.mark.unit
class TestRegister:

    async def test_raises_when_already_registered(self, service, detail_repo_mock):
        detail_repo_mock.exists_by_customer.return_value = True
        with pytest.raises(CustomerAlreadyRegisteredError):
            await service.register(
                customer_email="alice@example.com",
                nickname="a", phone_number="01000000000",
                preferred_menus=None,
                nutrition_types=None,
                allergies=None,
                topping_types=None,
            )


    async def test_saves_detail_and_all_preferences(
        self, service, detail_repo_mock, menu_repo_mock, nutrition_repo_mock,
        allergy_repo_mock, topping_repo_mock,
    ):
        detail_repo_mock.exists_by_customer.return_value = False
        # save_bulk 가 echo 식으로 동작 — 받은 menu_types 길이만큼 dummy 리스트 반환.
        menu_repo_mock.save_bulk.side_effect = lambda email, items: items
        nutrition_repo_mock.save_bulk.side_effect = lambda email, items: items
        allergy_repo_mock.save_bulk.side_effect = lambda email, items: items
        topping_repo_mock.save_bulk.side_effect = lambda email, items: items

        detail, menus, nutritions, allergies, toppings = await service.register(
            customer_email="alice@example.com",
            nickname="홍길동", phone_number="01012345678",
            preferred_menus=[PreferredMenu.salad, PreferredMenu.korean],
            nutrition_types=[NutritionType.protein],
            allergies=[AllergyType.peanut],
            topping_types=[ToppingType.avocado],
        )

        detail_repo_mock.save.assert_awaited_once()
        assert detail.nickname == "홍길동"
        assert detail.phone_number == "01012345678"
        assert len(menus) == 2
        assert len(nutritions) == 1
        assert len(allergies) == 1
        assert len(toppings) == 1


    async def test_skips_save_bulk_for_none_preferences(
        self, service, detail_repo_mock, menu_repo_mock,
        nutrition_repo_mock, allergy_repo_mock, topping_repo_mock,
    ):
        detail_repo_mock.exists_by_customer.return_value = False

        result = await service.register(
            customer_email="alice@example.com",
            nickname="x", phone_number="01000000000",
            preferred_menus=None,
            nutrition_types=None,
            allergies=None,
            topping_types=None,
        )

        _, menus, nutritions, allergies, toppings = result
        assert menus == [] and nutritions == [] and allergies == [] and toppings == []
        menu_repo_mock.save_bulk.assert_not_awaited()
        nutrition_repo_mock.save_bulk.assert_not_awaited()
        allergy_repo_mock.save_bulk.assert_not_awaited()
        topping_repo_mock.save_bulk.assert_not_awaited()
