import pytest

from app.domain.customer.service.customer_preference import CustomerPreferenceService

from test.unit.domain.customer.customer_preference_service.mock_factory import (
    AllergyRepoMockFactory,
    FakeUnitOfWork,
    MenuRepoMockFactory,
    NutritionRepoMockFactory,
    ToppingRepoMockFactory,
    make_mock_session,
)


@pytest.fixture
def mock_session():
    return make_mock_session()


@pytest.fixture
def menu_repo_mock():
    return MenuRepoMockFactory.create()


@pytest.fixture
def nutrition_repo_mock():
    return NutritionRepoMockFactory.create()


@pytest.fixture
def allergy_repo_mock():
    return AllergyRepoMockFactory.create()


@pytest.fixture
def topping_repo_mock():
    return ToppingRepoMockFactory.create()


@pytest.fixture
def service(
    monkeypatch, mock_session,
    menu_repo_mock, nutrition_repo_mock, allergy_repo_mock, topping_repo_mock,
):
    monkeypatch.setattr(
        "app.domain.customer.service.customer_preference.CustomerPreferredMenuRepository",
        lambda s: menu_repo_mock,
    )
    monkeypatch.setattr(
        "app.domain.customer.service.customer_preference.CustomerNutritionTypeRepository",
        lambda s: nutrition_repo_mock,
    )
    monkeypatch.setattr(
        "app.domain.customer.service.customer_preference.CustomerAllergyRepository",
        lambda s: allergy_repo_mock,
    )
    monkeypatch.setattr(
        "app.domain.customer.service.customer_preference.CustomerToppingTypeRepository",
        lambda s: topping_repo_mock,
    )
    return CustomerPreferenceService(uow=FakeUnitOfWork(mock_session))
