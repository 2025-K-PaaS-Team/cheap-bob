from unittest.mock import AsyncMock
from test.unit.domain.order.seller_order_service.mock_factory import (
    FakeUnitOfWork,
    HistoryRepoMockFactory,
    InternalPaymentClientMockFactory,
    OrderCurrentItemRepoMockFactory,
    OrderQueryServiceMockFactory,
    SellerProductServiceMockFactory,
    StoreReadServiceMockFactory,
    make_mock_session,
)
from test.unit.domain.order.customer_order_service.model_factory import (
    CustomerDetailFactory,
    CustomerFactory,
    OrderFactory,
    OrderHistoryFactory,
    ProductFactory,
    StoreFactory,
)
import pytest

from app.domain.order.service.seller_order import SellerOrderService


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
def payment_client_mock():
    return InternalPaymentClientMockFactory.create()


@pytest.fixture
def enqueue_event_mock(monkeypatch):
    """워커가 outbox 이벤트를 발행하는지 검증 — sync 환불 루프 이벤트화 검증."""
    mock = AsyncMock()
    monkeypatch.setattr(
        "app.domain.order.service.seller_order.enqueue_event", mock,
    )
    return mock


@pytest.fixture
def service(
    monkeypatch,
    mock_session,
    order_repo_mock,
    history_repo_mock,
    store_read_mock,
    product_service_mock,
    order_query_mock,
    payment_client_mock,
    enqueue_event_mock,
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
        internal_payment_client=payment_client_mock,
    )
