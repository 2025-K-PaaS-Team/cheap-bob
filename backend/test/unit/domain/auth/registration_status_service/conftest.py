import pytest

from app.domain.auth.service.registration_status import RegistrationStatusService

from test.unit.domain.auth.registration_status_service.mock_factory import (
    CustomerStatusServiceMockFactory,
    FakeUnitOfWork,
    SellerStatusServiceMockFactory,
)


@pytest.fixture
def customer_status_mock():
    return CustomerStatusServiceMockFactory.create()


@pytest.fixture
def seller_status_mock():
    return SellerStatusServiceMockFactory.create()


@pytest.fixture
def service(customer_status_mock, seller_status_mock):
    return RegistrationStatusService(
        uow=FakeUnitOfWork(),
        customer_registration_status_service=customer_status_mock,
        seller_registration_status_service=seller_status_mock,
    )
