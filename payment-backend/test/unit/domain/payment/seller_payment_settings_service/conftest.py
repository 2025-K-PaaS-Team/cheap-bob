from test.unit.domain.payment.seller_payment_settings_service.mock_factory import (
    StorePaymentInfoServiceMockFactory,
)
import pytest

from app.domain.payment.service.seller_payment_settings import (
    SellerPaymentSettingsService,
)


@pytest.fixture
def store_payment_info_mock():
    return StorePaymentInfoServiceMockFactory.create()


@pytest.fixture
def service(store_payment_info_mock):
    return SellerPaymentSettingsService(
        store_payment_info_service=store_payment_info_mock,
    )
