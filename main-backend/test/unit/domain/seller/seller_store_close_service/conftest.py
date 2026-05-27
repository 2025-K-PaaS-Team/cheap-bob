from unittest.mock import AsyncMock
from test.unit.domain.seller.seller_store_close_service.mock_factory import (
    FakeUnitOfWork,
    InternalPaymentClientMockFactory,
    OperationRepoMockFactory,
    OrderQueryServiceMockFactory,
    make_mock_session,
)
import pytest

from app.domain.seller.service.seller_store_close import SellerStoreCloseService


@pytest.fixture
def mock_session():
    return make_mock_session()


@pytest.fixture
def operation_repo_mock():
    return OperationRepoMockFactory.create()


@pytest.fixture
def order_query_mock():
    return OrderQueryServiceMockFactory.create()


@pytest.fixture
def payment_client_mock():
    return InternalPaymentClientMockFactory.create()


@pytest.fixture
def enqueue_event_mock(monkeypatch):
    """환불 요청 outbox 발행 검증 — sync 환불 루프가 이벤트로 대체됨."""
    mock = AsyncMock()
    monkeypatch.setattr(
        "app.domain.seller.service.seller_store_close.enqueue_event", mock,
    )
    return mock


@pytest.fixture
def service(
    monkeypatch, mock_session,
    operation_repo_mock, order_query_mock, payment_client_mock, enqueue_event_mock,
):
    monkeypatch.setattr(
        "app.domain.seller.service.seller_store_close.StoreOperationInfoRepository",
        lambda s: operation_repo_mock,
    )
    return SellerStoreCloseService(
        uow=FakeUnitOfWork(mock_session),
        order_query_service=order_query_mock,
        internal_payment_client=payment_client_mock,
    )
