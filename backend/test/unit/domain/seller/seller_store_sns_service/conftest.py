import pytest

from app.domain.seller.service.seller_store_sns import SellerStoreSNSService

from test.unit.domain.seller.seller_store_sns_service.mock_factory import (
    FakeUnitOfWork,
    StoreSNSRepoMockFactory,
    make_mock_session,
)


@pytest.fixture
def mock_session():
    return make_mock_session()


@pytest.fixture
def sns_repo_mock():
    return StoreSNSRepoMockFactory.create()


@pytest.fixture
def service(monkeypatch, mock_session, sns_repo_mock):
    monkeypatch.setattr(
        "app.domain.seller.service.seller_store_sns.StoreSNSRepository",
        lambda s: sns_repo_mock,
    )
    return SellerStoreSNSService(uow=FakeUnitOfWork(mock_session))
