from unittest.mock import AsyncMock
from types import SimpleNamespace
import pytest

from test.unit.domain.order.refund_completed_event_handler.mock_factory import (
    FakeUnitOfWork,
    OrderCurrentItemRepoMockFactory,
    ProcessedEventRepoMockFactory,
    SellerProductServiceMockFactory,
    make_mock_session,
)

from app.domain.order.event.refund_completed_handler import (
    PaymentRefundCompletedEventHandler,
)


@pytest.fixture
def mock_session():
    return make_mock_session()


@pytest.fixture
def seller_product_mock():
    return SellerProductServiceMockFactory.create()


@pytest.fixture
def order_repo_mock():
    return OrderCurrentItemRepoMockFactory.create()


@pytest.fixture
def processed_event_repo_mock():
    return ProcessedEventRepoMockFactory.create()


@pytest.fixture
def send_email_mock(monkeypatch):
    """tx 밖에서 호출되는 cancel 이메일 함수를 mock — 호출 여부 검증용."""
    mock = AsyncMock()
    monkeypatch.setattr(
        "app.domain.order.event.refund_completed_handler.send_seller_cancel_email",
        mock,
    )
    return mock


@pytest.fixture
def handler(
    monkeypatch, mock_session,
    seller_product_mock, order_repo_mock, processed_event_repo_mock,
):
    monkeypatch.setattr(
        "app.domain.order.event.refund_completed_handler.ProcessedEventRepository",
        lambda session: processed_event_repo_mock,
    )
    monkeypatch.setattr(
        "app.domain.order.event.refund_completed_handler.OrderCurrentItemRepository",
        lambda session: order_repo_mock,
    )
    return PaymentRefundCompletedEventHandler(
        uow=FakeUnitOfWork(mock_session),
        seller_product_service=seller_product_mock,
    )


@pytest.fixture
def v2_payload():
    return {
        "payment_id": "PAY_test",
        "store_id": "STR_x",
        "store_name": "테스트 가게",
        "customer_id": "buyer@example.com",
        "product_id": "PRD_x",
        "quantity": 2,
        "reason": "테스트 환불",
    }


@pytest.fixture
def fixed_event_id():
    return "11111111-1111-1111-1111-111111111111"


@pytest.fixture
def msg(v2_payload, fixed_event_id):
    return SimpleNamespace(
        headers=[("event_id", fixed_event_id.encode("utf-8"))],
        value=v2_payload,
        offset=42,
    )
