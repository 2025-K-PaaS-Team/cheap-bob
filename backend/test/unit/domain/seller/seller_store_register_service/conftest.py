import pytest

from app.domain.seller.service.seller_store_register import SellerStoreRegisterService

from test.unit.domain.seller.seller_store_register_service.mock_factory import (
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
        "app.domain.seller.service.seller_store_register.StoreRepository",
        lambda s: store_repo_mock,
    )
    # generate_store_id 는 고정값으로.
    monkeypatch.setattr(
        "app.domain.seller.service.seller_store_register.generate_store_id",
        lambda: "STR_fixed",
    )
    return SellerStoreRegisterService(uow=FakeUnitOfWork(mock_session))
