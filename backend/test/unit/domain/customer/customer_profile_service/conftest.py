from test.unit.domain.customer.customer_profile_service.mock_factory import (
    CustomerProfileRepoMocks,
    FakeUnitOfWork,
    make_mock_session,
)
import pytest

from app.domain.customer.service.customer_profile import CustomerProfileService


@pytest.fixture
def mock_session():
    return make_mock_session()


@pytest.fixture
def profile_repos():
    return CustomerProfileRepoMocks()


@pytest.fixture
def service(monkeypatch, mock_session, profile_repos):
    monkeypatch.setattr(
        "app.domain.customer.service.customer_profile.CustomerDetailRepository",
        lambda session: profile_repos.detail,
    )
    monkeypatch.setattr(
        "app.domain.customer.service.customer_profile.CustomerPreferredMenuRepository",
        lambda session: profile_repos.preferred_menus,
    )
    monkeypatch.setattr(
        "app.domain.customer.service.customer_profile.CustomerNutritionTypeRepository",
        lambda session: profile_repos.nutrition_types,
    )
    monkeypatch.setattr(
        "app.domain.customer.service.customer_profile.CustomerAllergyRepository",
        lambda session: profile_repos.allergies,
    )
    monkeypatch.setattr(
        "app.domain.customer.service.customer_profile.CustomerToppingTypeRepository",
        lambda session: profile_repos.topping_types,
    )
    return CustomerProfileService(uow=FakeUnitOfWork(mock_session))
