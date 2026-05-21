import pytest

from app.domain.payment.service.payment_gateway import PaymentGatewayService


@pytest.fixture
def service() -> PaymentGatewayService:
    return PaymentGatewayService()
