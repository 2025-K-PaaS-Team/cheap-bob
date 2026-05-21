import pytest

from app.domain.customer.service.customer_profile import CustomerProfileService

from test.unit.domain.customer.customer_profile_service.mock_factory import (
    CustomerProfileRepoMockFactory,
    FakeUnitOfWork,
    make_mock_session,
)


@pytest.fixture
def mock_session():
    return make_mock_session()


@pytest.fixture
def profile_repo_mock():
    return CustomerProfileRepoMockFactory.create()


@pytest.fixture
def service(monkeypatch, mock_session, profile_repo_mock):
    monkeypatch.setattr(
        "app.domain.customer.service.customer_profile.CustomerProfileRepository",
        lambda session: profile_repo_mock,
    )
    return CustomerProfileService(uow=FakeUnitOfWork(mock_session))
