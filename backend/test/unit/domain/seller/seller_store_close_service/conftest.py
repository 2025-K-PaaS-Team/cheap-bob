from test.unit.domain.seller.seller_store_close_service.mock_factory import (
    FakeUnitOfWork,
    OperationRepoMockFactory,
    OrderQueryServiceMockFactory,
    PaymentGatewayServiceMockFactory,
    SellerProductServiceMockFactory,
    StorePaymentInfoServiceMockFactory,
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
def payment_gateway_mock():
    return PaymentGatewayServiceMockFactory.create()


@pytest.fixture
def payment_info_mock():
    return StorePaymentInfoServiceMockFactory.create()


@pytest.fixture
def service(
    monkeypatch, mock_session,
    operation_repo_mock, order_query_mock,
    product_service_mock, payment_gateway_mock, payment_info_mock,
):
    monkeypatch.setattr(
        "app.domain.seller.service.seller_store_close.StoreOperationInfoRepository",
        lambda s: operation_repo_mock,
    )
    return SellerStoreCloseService(
        uow=FakeUnitOfWork(mock_session),
        order_query_service=order_query_mock,
        seller_product_service=product_service_mock,
        payment_gateway_service=payment_gateway_mock,
        store_payment_info_service=payment_info_mock,
    )
