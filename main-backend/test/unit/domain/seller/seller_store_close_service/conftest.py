from test.unit.domain.seller.seller_store_close_service.mock_factory import (
    FakeUnitOfWork,
    InternalPaymentClientMockFactory,
    OperationRepoMockFactory,
    OrderQueryServiceMockFactory,
    SellerProductServiceMockFactory,
    make_mock_session,
)
import pytest

from app.domain.seller.service.seller_store_close import SellerStoreCloseService


@pytest.fixture
def mock_session():
    return make_mock_session()


@pytest.fixture
def operation_repo_mock():
    return OperationRepoMockFactory.create()


@pytest.fixture
def order_query_mock():
    return OrderQueryServiceMockFactory.create()


@pytest.fixture
def product_service_mock():
    return SellerProductServiceMockFactory.create()


@pytest.fixture
def payment_client_mock():
    return InternalPaymentClientMockFactory.create()


@pytest.fixture
def service(
    monkeypatch, mock_session,
    operation_repo_mock, order_query_mock,
    product_service_mock, payment_client_mock,
):
    monkeypatch.setattr(
        "app.domain.seller.service.seller_store_close.StoreOperationInfoRepository",
        lambda s: operation_repo_mock,
    )
    return SellerStoreCloseService(
        uow=FakeUnitOfWork(mock_session),
        order_query_service=order_query_mock,
        seller_product_service=product_service_mock,
        internal_payment_client=payment_client_mock,
    )
