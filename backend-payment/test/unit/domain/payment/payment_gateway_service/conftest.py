from unittest.mock import AsyncMock
import pytest

from app.domain.payment.service.payment_gateway import PaymentGatewayService


@pytest.fixture
def portone_client_mock() -> AsyncMock:
    """PortOnePaymentClient mock — fetch_payment / cancel_payment 둘 다 AsyncMock."""
    return AsyncMock()


@pytest.fixture
def service(portone_client_mock: AsyncMock) -> PaymentGatewayService:
    return PaymentGatewayService(portone_client=portone_client_mock)
