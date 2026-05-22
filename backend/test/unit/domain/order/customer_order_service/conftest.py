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
    OrderCurrentItemRepoMockFactory,
    PaymentGatewayServiceMockFactory,
    SellerProductServiceMockFactory,
    SellerStoreImageServiceMockFactory,
    SellerStoreReadServiceMockFactory,
    StorePaymentInfoServiceMockFactory,
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
    store_image_mock,
    product_service_mock,
    payment_gateway_mock,
    store_payment_info_mock,
):
    # `@transactional` 메서드 내부에서 ``OrderCurrentItemRepository(self._session)`` 호출
    # — 모듈 레벨 이름을 lambda 로 치환한다.
    monkeypatch.setattr(
        "app.domain.order.service.customer_order.OrderCurrentItemRepository",
        lambda session: order_repo_mock,
    )
    # 이메일 전송은 background_tasks 에 등록만 되므로 호출 자체는 일어나지 않지만,
    # 안전을 위해 import 경로를 no-op 으로 치환.
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
        payment_gateway_service=payment_gateway_mock,
        store_payment_info_service=store_payment_info_mock,
    )
