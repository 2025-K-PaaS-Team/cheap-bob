from test.unit.domain.customer.customer_account_service.mock_factory import (
    CustomerRepoMockFactory,
    FakeUnitOfWork,
    make_mock_session,
)
import pytest

from app.domain.customer.service.customer_account import CustomerAccountService


@pytest.fixture
def mock_session():
    return make_mock_session()


@pytest.fixture
def repo_mock():
    return CustomerRepoMockFactory.create()


@pytest.fixture
def service(monkeypatch, mock_session, repo_mock):
    monkeypatch.setattr(
        "app.domain.customer.service.customer_account.CustomerRepository",
        lambda session: repo_mock,
    )
    return CustomerAccountService(uow=FakeUnitOfWork(mock_session))
