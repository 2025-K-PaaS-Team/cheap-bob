import pytest

from app.domain.payment.service.customer_payment import CustomerPaymentService

from test.unit.domain.payment.customer_payment_service.model_factory import (
    CartItemFactory,
    OperationInfoFactory,
    PaymentInfoFactory,
    ProductFactory,
)
from test.unit.domain.payment.customer_payment_service.mock_factory import (
    CartItemRepoMockFactory,
    CustomerProfileServiceMockFactory,
    FakeUnitOfWork,
    OrderQueryServiceMockFactory,
    PaymentGatewayServiceMockFactory,
    SellerProductServiceMockFactory,
    SellerStoreReadServiceMockFactory,
    StorePaymentInfoServiceMockFactory,
    make_mock_session,
)


@pytest.fixture(autouse=True)
def reset_factories():
    for f in (ProductFactory, CartItemFactory):
        f.reset_counter()
    yield
    for f in (ProductFactory, CartItemFactory):
        f.reset_counter()


@pytest.fixture
def mock_session():
    return make_mock_session()


@pytest.fixture
def store_read_mock():
    return SellerStoreReadServiceMockFactory.create()


@pytest.fixture
def product_service_mock():
    return SellerProductServiceMockFactory.create()


@pytest.fixture
def store_payment_info_mock():
    return StorePaymentInfoServiceMockFactory.create()


@pytest.fixture
def payment_gateway_mock():
    return PaymentGatewayServiceMockFactory.create()


@pytest.fixture
def order_query_mock():
    return OrderQueryServiceMockFactory.create()


@pytest.fixture
def customer_profile_mock():
    return CustomerProfileServiceMockFactory.create()


@pytest.fixture
def cart_repo_mock(monkeypatch):
    """``sweep_expired_carts`` 내부의 ``CartItemRepository(self._session)`` 를 가로채는 fixture.

    service 가 함수 내부에서 ``from app.domain.order.repository.cart_item import
    CartItemRepository`` 한 뒤 즉시 ``CartItemRepository(self._session)`` 로 construct
    하므로, 본 fixture 는 해당 클래스 자체를 호출 시 fake repo 를 반환하는 callable 로
    교체한다.
    """
    repo = CartItemRepoMockFactory.create()
    import app.domain.order.repository.cart_item as cart_item_mod
    monkeypatch.setattr(cart_item_mod, "CartItemRepository", lambda _s: repo)
    return repo


@pytest.fixture
def service(
    mock_session,
    store_read_mock,
    product_service_mock,
    store_payment_info_mock,
    payment_gateway_mock,
    order_query_mock,
    customer_profile_mock,
):
    return CustomerPaymentService(
        uow=FakeUnitOfWork(mock_session),
        seller_store_read_service=store_read_mock,
        seller_product_service=product_service_mock,
        store_payment_info_service=store_payment_info_mock,
        payment_gateway_service=payment_gateway_mock,
        order_query_service=order_query_mock,
        customer_profile_service=customer_profile_mock,
    )
