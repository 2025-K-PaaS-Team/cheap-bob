import pytest

from app.domain.order.service.seller_order import SellerOrderService

from test.unit.domain.order.customer_order_service.model_factory import (
    CustomerDetailFactory,
    CustomerFactory,
    OrderFactory,
    OrderHistoryFactory,
    ProductFactory,
    StoreFactory,
)
from test.unit.domain.order.seller_order_service.mock_factory import (
    FakeUnitOfWork,
    HistoryRepoMockFactory,
    OrderCurrentItemRepoMockFactory,
    OrderQueryServiceMockFactory,
    PaymentGatewayServiceMockFactory,
    SellerProductServiceMockFactory,
    StorePaymentInfoServiceMockFactory,
    StoreReadServiceMockFactory,
    make_mock_session,
)


@pytest.fixture(autouse=True)
def reset_factories():
    for f in (CustomerDetailFactory, CustomerFactory, StoreFactory, ProductFactory,
              OrderFactory, OrderHistoryFactory):
        f.reset_counter()
    yield
    for f in (CustomerDetailFactory, CustomerFactory, StoreFactory, ProductFactory,
              OrderFactory, OrderHistoryFactory):
        f.reset_counter()


@pytest.fixture
def mock_session():
    return make_mock_session()


@pytest.fixture
def order_repo_mock():
    return OrderCurrentItemRepoMockFactory.create()


@pytest.fixture
def history_repo_mock():
    return HistoryRepoMockFactory.create()


@pytest.fixture
def store_read_mock():
    return StoreReadServiceMockFactory.create()


@pytest.fixture
def product_service_mock():
    return SellerProductServiceMockFactory.create()


@pytest.fixture
def order_query_mock():
    return OrderQueryServiceMockFactory.create()


@pytest.fixture
def payment_gateway_mock():
    return PaymentGatewayServiceMockFactory.create()


@pytest.fixture
def store_payment_info_mock():
    return StorePaymentInfoServiceMockFactory.create()


@pytest.fixture
def service(
    monkeypatch,
    mock_session,
    order_repo_mock,
    history_repo_mock,
    store_read_mock,
    product_service_mock,
    order_query_mock,
    payment_gateway_mock,
    store_payment_info_mock,
):
    monkeypatch.setattr(
        "app.domain.order.service.seller_order.OrderCurrentItemRepository",
        lambda session: order_repo_mock,
    )
    return SellerOrderService(
        uow=FakeUnitOfWork(mock_session),
        history_repo=history_repo_mock,
        seller_store_read_service=store_read_mock,
        seller_product_service=product_service_mock,
        order_query_service=order_query_mock,
        payment_gateway_service=payment_gateway_mock,
        store_payment_info_service=store_payment_info_mock,
    )
