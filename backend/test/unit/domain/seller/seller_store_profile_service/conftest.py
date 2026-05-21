import pytest

from app.domain.seller.service.seller_store_profile import SellerStoreProfileService

from test.unit.domain.seller.seller_store_profile_service.mock_factory import (
    FakeUnitOfWork,
    StoreRepoMockFactory,
    make_mock_session,
)


@pytest.fixture
def mock_session():
    return make_mock_session()


@pytest.fixture
def store_repo_mock():
    return StoreRepoMockFactory.create()


@pytest.fixture
def service(monkeypatch, mock_session, store_repo_mock):
    monkeypatch.setattr(
        "app.domain.seller.service.seller_store_profile.StoreRepository",
        lambda s: store_repo_mock,
    )
    return SellerStoreProfileService(uow=FakeUnitOfWork(mock_session))
