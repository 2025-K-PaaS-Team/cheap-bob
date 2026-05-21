import pytest

from app.domain.auth.service.account import AuthAccountService

from test.unit.domain.auth.account_service.mock_factory import (
    CustomerRepositoryMockFactory,
    FakeUnitOfWork,
    SellerRepositoryMockFactory,
    make_mock_session,
)


@pytest.fixture
def mock_session():
    return make_mock_session()


@pytest.fixture
def customer_repo_mock():
    return CustomerRepositoryMockFactory.create()


@pytest.fixture
def seller_repo_mock():
    return SellerRepositoryMockFactory.create()


@pytest.fixture
def service(monkeypatch, mock_session, customer_repo_mock, seller_repo_mock):
    monkeypatch.setattr(
        "app.domain.auth.service.account.CustomerRepository",
        lambda session: customer_repo_mock,
    )
    monkeypatch.setattr(
        "app.domain.auth.service.account.SellerRepository",
        lambda session: seller_repo_mock,
    )
    return AuthAccountService(uow=FakeUnitOfWork(mock_session))
