import pytest

from app.domain.seller.service.seller_registration_status import (
    SellerRegistrationStatusService,
)

from test.unit.domain.seller.seller_registration_status_service.mock_factory import (
    FakeUnitOfWork,
    ProductRepoMockFactory,
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
def product_repo_mock():
    return ProductRepoMockFactory.create()


@pytest.fixture
def service(monkeypatch, mock_session, store_repo_mock, product_repo_mock):
    monkeypatch.setattr(
        "app.domain.seller.service.seller_registration_status.StoreRepository",
        lambda s: store_repo_mock,
    )
    monkeypatch.setattr(
        "app.domain.seller.service.seller_registration_status.StoreProductInfoRepository",
        lambda s: product_repo_mock,
    )
    return SellerRegistrationStatusService(uow=FakeUnitOfWork(mock_session))
