from test.unit.domain.order.customer_order_service.model_factory import (
    CustomerDetailFactory,
    CustomerFactory,
    OrderFactory,
    OrderHistoryFactory,
    ProductFactory,
    StoreFactory,
)
from test.unit.domain.order.customer_order_service.mock_factory import (
    FakeUnitOfWork,
    HistoryRepoMockFactory,
    InternalPaymentClientMockFactory,
    OrderCurrentItemRepoMockFactory,
    SellerProductServiceMockFactory,
    SellerStoreImageServiceMockFactory,
    SellerStoreReadServiceMockFactory,
    make_mock_session,
)
import pytest

from app.domain.order.service.customer_order import CustomerOrderService


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
    return SellerStoreReadServiceMockFactory.create()


@pytest.fixture
def store_image_mock():
    return SellerStoreImageServiceMockFactory.create()


@pytest.fixture
def product_service_mock():
    return SellerProductServiceMockFactory.create()


@pytest.fixture
def payment_client_mock():
    return InternalPaymentClientMockFactory.create()


@pytest.fixture
def service(
    monkeypatch,
    mock_session,
    order_repo_mock,
    history_repo_mock,
    store_read_mock,
    store_image_mock,
    product_service_mock,
    payment_client_mock,
):
    monkeypatch.setattr(
        "app.domain.order.service.customer_order.OrderCurrentItemRepository",
        lambda session: order_repo_mock,
    )
    monkeypatch.setattr(
        "app.core.email.notifier.send_customer_cancel_email",
        lambda *a, **kw: None, raising=False,
    )
    return CustomerOrderService(
        uow=FakeUnitOfWork(mock_session),
        history_repo=history_repo_mock,
        seller_store_read_service=store_read_mock,
        seller_store_image_service=store_image_mock,
        seller_product_service=product_service_mock,
        internal_payment_client=payment_client_mock,
    )
