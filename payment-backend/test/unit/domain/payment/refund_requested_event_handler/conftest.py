from uuid import UUID
from unittest.mock import AsyncMock
from test.unit.domain.payment.refund_requested_event_handler.mock_factory import (
    FakeUnitOfWork,
    PaymentGatewayServiceMockFactory,
    ProcessedEventRepoMockFactory,
    StorePaymentInfoServiceMockFactory,
    make_mock_session,
)
import pytest

from app.domain.payment.event.refund_requested_handler import (
    OrderRefundRequestedEventHandler,
)


@pytest.fixture
def mock_session():
    return make_mock_session()


@pytest.fixture
def store_payment_info_mock():
    return StorePaymentInfoServiceMockFactory.create()


@pytest.fixture
def payment_gateway_mock():
    return PaymentGatewayServiceMockFactory.create()


@pytest.fixture
def processed_event_repo_mock():
    return ProcessedEventRepoMockFactory.create()


@pytest.fixture
def enqueue_event_mock(monkeypatch):
    """outbox enqueue 검증 — handler 가 completed / failed 페이로드를 올바르게 만드는지."""
    mock = AsyncMock()
    monkeypatch.setattr(
        "app.domain.payment.event.refund_requested_handler.enqueue_event", mock,
    )
    return mock


@pytest.fixture
def handler(
    monkeypatch, mock_session,
    store_payment_info_mock, payment_gateway_mock,
    processed_event_repo_mock, enqueue_event_mock,
):
    # ProcessedEventRepository 를 mock 으로 대체.
    monkeypatch.setattr(
        "app.domain.payment.event.refund_requested_handler.ProcessedEventRepository",
        lambda session: processed_event_repo_mock,
    )
    return OrderRefundRequestedEventHandler(
        uow=FakeUnitOfWork(mock_session),
        store_payment_info_service=store_payment_info_mock,
        payment_gateway_service=payment_gateway_mock,
    )


# ───────── ConsumerRecord 빌더 ─────────


def _make_msg(*, event_id: str, payload: dict):
    """ConsumerRecord 의 최소 모양 — handler 가 쓰는 .headers / .value / .offset 만."""
    from types import SimpleNamespace
    return SimpleNamespace(
        headers=[("event_id", event_id.encode("utf-8"))],
        value=payload,
        offset=42,
    )


@pytest.fixture
def make_msg():
    return _make_msg


@pytest.fixture
def v2_payload():
    """v2 schema 필수 7 필드 모두 채운 payload."""
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
def msg(make_msg, v2_payload, fixed_event_id):
    return make_msg(event_id=fixed_event_id, payload=v2_payload)
