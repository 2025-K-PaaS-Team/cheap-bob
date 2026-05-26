from test.unit.domain.seller.seller_store_settings_service.mock_factory import (
    FakeUnitOfWork,
    InternalPaymentClientMockFactory,
    ModificationRepoMockFactory,
    OperationRepoMockFactory,
    StoreAddressRepoMockFactory,
    StoreRepoMockFactory,
    make_mock_session,
)
import pytest

from app.domain.seller.service.seller_store_settings import SellerStoreSettingsService


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
def operation_repo_mock():
    return OperationRepoMockFactory.create()


@pytest.fixture
def modification_repo_mock():
    return ModificationRepoMockFactory.create()


@pytest.fixture
def payment_client_mock():
    return InternalPaymentClientMockFactory.create()


@pytest.fixture
def service(
    monkeypatch, mock_session,
    store_repo_mock, address_repo_mock,
    operation_repo_mock, modification_repo_mock, payment_client_mock,
):
    monkeypatch.setattr(
        "app.domain.seller.service.seller_store_settings.StoreRepository",
        lambda s: store_repo_mock,
    )
    monkeypatch.setattr(
        "app.domain.seller.service.seller_store_settings.StoreAddressRepository",
        lambda s: address_repo_mock,
    )
    monkeypatch.setattr(
        "app.domain.seller.service.seller_store_settings.StoreOperationInfoRepository",
        lambda s: operation_repo_mock,
    )
    monkeypatch.setattr(
        "app.domain.seller.service.seller_store_settings.StoreOperationInfoModificationRepository",
        lambda s: modification_repo_mock,
    )
    return SellerStoreSettingsService(
        uow=FakeUnitOfWork(mock_session),
        internal_payment_client=payment_client_mock,
    )
