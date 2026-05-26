from test.unit.domain.seller.seller_account_service.mock_factory import (
    FakeUnitOfWork,
    SellerRepoMockFactory,
    make_mock_session,
)
import pytest

from app.domain.seller.service.seller_account import SellerAccountService


@pytest.fixture
def mock_session():
    return make_mock_session()


@pytest.fixture
def repo_mock():
    return SellerRepoMockFactory.create()


@pytest.fixture
def service(monkeypatch, mock_session, repo_mock):
    monkeypatch.setattr(
        "app.domain.seller.service.seller_account.SellerRepository",
        lambda session: repo_mock,
    )
    return SellerAccountService(uow=FakeUnitOfWork(mock_session))
