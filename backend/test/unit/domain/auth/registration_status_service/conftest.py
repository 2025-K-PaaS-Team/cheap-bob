from test.unit.domain.auth.registration_status_service.mock_factory import (
    CustomerStatusServiceMockFactory,
    SellerStatusServiceMockFactory,
)
import pytest

from app.domain.auth.service.registration_status import RegistrationStatusService


@pytest.fixture
def customer_status_mock():
    return CustomerStatusServiceMockFactory.create()


@pytest.fixture
def seller_status_mock():
    return SellerStatusServiceMockFactory.create()


@pytest.fixture
def service(customer_status_mock, seller_status_mock):
    return RegistrationStatusService(
        customer_registration_status_service=customer_status_mock,
        seller_registration_status_service=seller_status_mock,
    )
