from test.unit.domain.seller.seller_store_register_service.mock_factory import (
    FakeUnitOfWork,
    StoreAddressRepoMockFactory,
    StoreOperationRepoMockFactory,
    StoreRepoMockFactory,
    StoreSNSRepoMockFactory,
    make_mock_session,
)
import pytest

from app.domain.seller.service.seller_store_register import SellerStoreRegisterService


@pytest.fixture
def mock_session():
    return make_mock_session()


@pytest.fixture
def store_repo_mock():
    return StoreRepoMockFactory.create()


@pytest.fixture
def address_repo_mock():
    return StoreAddressRepoMockFactory.create()


@pytest.fixture
def sns_repo_mock():
    return StoreSNSRepoMockFactory.create()


@pytest.fixture
def operation_repo_mock():
    return StoreOperationRepoMockFactory.create()


@pytest.fixture
def service(
    monkeypatch, mock_session,
    store_repo_mock, address_repo_mock, sns_repo_mock, operation_repo_mock,
):
    monkeypatch.setattr(
        "app.domain.seller.service.seller_store_register.StoreRepository",
        lambda s: store_repo_mock,
    )
    monkeypatch.setattr(
        "app.domain.seller.service.seller_store_register.StoreAddressRepository",
        lambda s: address_repo_mock,
    )
    monkeypatch.setattr(
        "app.domain.seller.service.seller_store_register.StoreSNSRepository",
        lambda s: sns_repo_mock,
    )
    monkeypatch.setattr(
        "app.domain.seller.service.seller_store_register.StoreOperationInfoRepository",
        lambda s: operation_repo_mock,
    )
    monkeypatch.setattr(
        "app.domain.seller.service.seller_store_register.generate_store_id",
        lambda: "STR_fixed",
    )
    return SellerStoreRegisterService(uow=FakeUnitOfWork(mock_session))
