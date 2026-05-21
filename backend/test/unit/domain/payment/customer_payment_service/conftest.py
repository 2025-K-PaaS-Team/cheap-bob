import pytest

from app.domain.payment.service.customer_payment import CustomerPaymentService

from test.unit.domain.payment.customer_payment_service.model_factory import (
    CartItemFactory,
    OperationInfoFactory,
    PaymentInfoFactory,
    ProductFactory,
)
from test.unit.domain.payment.customer_payment_service.mock_factory import (
    CustomerProfileServiceMockFactory,
    FakeUnitOfWork,
    OrderQueryServiceMockFactory,
    PaymentGatewayServiceMockFactory,
    PaymentSchedulerServiceMockFactory,
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
def payment_scheduler_mock():
    return PaymentSchedulerServiceMockFactory.create()


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
def service(
    mock_session,
    store_read_mock,
    product_service_mock,
    store_payment_info_mock,
    payment_scheduler_mock,
    payment_gateway_mock,
    order_query_mock,
    customer_profile_mock,
):
    return CustomerPaymentService(
        uow=FakeUnitOfWork(mock_session),
        seller_store_read_service=store_read_mock,
        seller_product_service=product_service_mock,
        store_payment_info_service=store_payment_info_mock,
        payment_scheduler_service=payment_scheduler_mock,
        payment_gateway_service=payment_gateway_mock,
        order_query_service=order_query_mock,
        customer_profile_service=customer_profile_mock,
    )
