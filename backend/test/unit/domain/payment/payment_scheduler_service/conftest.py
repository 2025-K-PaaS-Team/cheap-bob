import pytest

from app.domain.payment.service.payment_scheduler import PaymentSchedulerService

from test.unit.domain.payment.payment_scheduler_service.mock_factory import (
    APSchedulerMockFactory,
    OrderQueryServiceMockFactory,
    SellerProductServiceMockFactory,
)


@pytest.fixture
def scheduler_mock():
    return APSchedulerMockFactory.create()


@pytest.fixture
def product_service_mock():
    return SellerProductServiceMockFactory.create()


@pytest.fixture
def order_query_mock():
    return OrderQueryServiceMockFactory.create()


@pytest.fixture
def service(scheduler_mock, product_service_mock, order_query_mock):
    return PaymentSchedulerService(
        scheduler=scheduler_mock,
        seller_product_service=product_service_mock,
        order_query_service=order_query_mock,
    )
