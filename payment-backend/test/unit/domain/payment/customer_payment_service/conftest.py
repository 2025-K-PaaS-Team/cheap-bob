from test.unit.domain.payment.customer_payment_service.model_factory import (
    CartItemFactory,
    ProductFactory,
)
from test.unit.domain.payment.customer_payment_service.mock_factory import (
    CartItemServiceMockFactory,
    FakeUnitOfWork,
    InternalOrderClientMockFactory,
    InternalSellerClientMockFactory,
    PaymentGatewayServiceMockFactory,
    StorePaymentInfoServiceMockFactory,
    make_mock_session,
)
import pytest

from app.domain.payment.service.customer_payment import CustomerPaymentService


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
def store_payment_info_mock():
    return StorePaymentInfoServiceMockFactory.create()


@pytest.fixture
def payment_gateway_mock():
    return PaymentGatewayServiceMockFactory.create()


@pytest.fixture
def cart_item_service_mock():
    return CartItemServiceMockFactory.create()


@pytest.fixture
def seller_client_mock():
    return InternalSellerClientMockFactory.create()


@pytest.fixture
def order_client_mock():
    return InternalOrderClientMockFactory.create()


@pytest.fixture
def service(
    mock_session,
    store_payment_info_mock,
    payment_gateway_mock,
    cart_item_service_mock,
    seller_client_mock,
    order_client_mock,
):
    return CustomerPaymentService(
        uow=FakeUnitOfWork(mock_session),
        store_payment_info_service=store_payment_info_mock,
        payment_gateway_service=payment_gateway_mock,
        cart_item_service=cart_item_service_mock,
        internal_seller_client=seller_client_mock,
        internal_order_client=order_client_mock,
    )
