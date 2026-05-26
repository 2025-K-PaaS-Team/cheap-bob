from test.unit.domain.auth.oauth_service.mock_factory import (
    CustomerAccountServiceMockFactory,
    JwtServiceMockFactory,
    SellerAccountServiceMockFactory,
)
import pytest

from app.domain.auth.service.oauth import OAuthService


@pytest.fixture
def customer_account_mock():
    return CustomerAccountServiceMockFactory.create()


@pytest.fixture
def seller_account_mock():
    return SellerAccountServiceMockFactory.create()


@pytest.fixture
def jwt_service_mock():
    return JwtServiceMockFactory.create()


@pytest.fixture
def service(customer_account_mock, seller_account_mock, jwt_service_mock):
    return OAuthService(
        jwt_service=jwt_service_mock,
        customer_account_service=customer_account_mock,
        seller_account_service=seller_account_mock,
    )
