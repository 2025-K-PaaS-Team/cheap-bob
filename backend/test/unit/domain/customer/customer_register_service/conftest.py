from test.unit.domain.customer.customer_register_service.mock_factory import (
    AllergyRepoMockFactory,
    DetailRepoMockFactory,
    FakeUnitOfWork,
    NutritionTypeRepoMockFactory,
    PreferredMenuRepoMockFactory,
    ToppingTypeRepoMockFactory,
    make_mock_session,
)
import pytest

from app.domain.customer.service.customer_register import CustomerRegisterService


@pytest.fixture
def mock_session():
    return make_mock_session()


@pytest.fixture
def detail_repo_mock():
    return DetailRepoMockFactory.create()


@pytest.fixture
def menu_repo_mock():
    return PreferredMenuRepoMockFactory.create()


@pytest.fixture
def nutrition_repo_mock():
    return NutritionTypeRepoMockFactory.create()


@pytest.fixture
def allergy_repo_mock():
    return AllergyRepoMockFactory.create()


@pytest.fixture
def topping_repo_mock():
    return ToppingTypeRepoMockFactory.create()


@pytest.fixture
def service(
    monkeypatch, mock_session,
    detail_repo_mock, menu_repo_mock, nutrition_repo_mock,
    allergy_repo_mock, topping_repo_mock,
):
    monkeypatch.setattr(
        "app.domain.customer.service.customer_register.CustomerDetailRepository",
        lambda s: detail_repo_mock,
    )
    monkeypatch.setattr(
        "app.domain.customer.service.customer_register.CustomerPreferredMenuRepository",
        lambda s: menu_repo_mock,
    )
    monkeypatch.setattr(
        "app.domain.customer.service.customer_register.CustomerNutritionTypeRepository",
        lambda s: nutrition_repo_mock,
    )
    monkeypatch.setattr(
        "app.domain.customer.service.customer_register.CustomerAllergyRepository",
        lambda s: allergy_repo_mock,
    )
    monkeypatch.setattr(
        "app.domain.customer.service.customer_register.CustomerToppingTypeRepository",
        lambda s: topping_repo_mock,
    )
    return CustomerRegisterService(uow=FakeUnitOfWork(mock_session))
