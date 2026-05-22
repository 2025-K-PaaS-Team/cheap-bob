from test.unit.domain.payment.store_payment_info_service.mock_factory import (
    FakeUnitOfWork,
    StorePaymentInfoRepoMockFactory,
    make_mock_session,
)
import pytest

from app.domain.payment.service.store_payment_info import StorePaymentInfoService


@pytest.fixture
def mock_session():
    return make_mock_session()


@pytest.fixture
def payment_repo_mock():
    return StorePaymentInfoRepoMockFactory.create()


@pytest.fixture
def service(monkeypatch, mock_session, payment_repo_mock):
    monkeypatch.setattr(
        "app.domain.payment.service.store_payment_info.StorePaymentInfoRepository",
        lambda s: payment_repo_mock,
    )
    return StorePaymentInfoService(uow=FakeUnitOfWork(mock_session))
