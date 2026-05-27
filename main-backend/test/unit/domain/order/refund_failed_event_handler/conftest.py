from unittest.mock import MagicMock
from types import SimpleNamespace
import pytest

from test.unit.domain.order.refund_failed_event_handler.mock_factory import (
    FakeUnitOfWork,
    ProcessedEventRepoMockFactory,
    make_mock_session,
)

from app.domain.order.event.refund_failed_handler import (
    PaymentRefundFailedEventHandler,
)


@pytest.fixture
def mock_session():
    return make_mock_session()


@pytest.fixture
def processed_event_repo_mock():
    return ProcessedEventRepoMockFactory.create()


@pytest.fixture
def mock_logger(monkeypatch):
    """loguru logger 를 MagicMock 으로 교체. CRITICAL alarm 검증용."""
    mock = MagicMock()
    monkeypatch.setattr(
        "app.domain.order.event.refund_failed_handler.logger", mock,
    )
    return mock


@pytest.fixture
def handler(monkeypatch, mock_session, processed_event_repo_mock):
    monkeypatch.setattr(
        "app.domain.order.event.refund_failed_handler.ProcessedEventRepository",
        lambda session: processed_event_repo_mock,
    )
    return PaymentRefundFailedEventHandler(uow=FakeUnitOfWork(mock_session))


# ───────── 메시지 빌더 ─────────


def _make_msg(*, event_id: str | None, payload):
    headers = []
    if event_id is not None:
        headers.append(("event_id", event_id.encode("utf-8")))
    return SimpleNamespace(
        headers=headers,
        value=payload,
        offset=42,
    )


@pytest.fixture
def make_msg():
    return _make_msg


@pytest.fixture
def fixed_event_id():
    return "11111111-1111-1111-1111-111111111111"


@pytest.fixture
def config_missing_payload():
    """가게 결제 설정 누락 경로의 failed payload."""
    return {
        "payment_id": "PAY_test",
        "store_id": "STR_x",
        "error_kind": "config_missing",
        "error_detail": "가게의 결제 설정이 완료되지 않았습니다",
    }


@pytest.fixture
def portone_refused_payload():
    return {
        "payment_id": "PAY_test2",
        "store_id": "STR_y",
        "error_kind": "portone_refused",
        "error_detail": "환불 처리 실패: PortOne cancel 401",
    }


@pytest.fixture
def msg(make_msg, config_missing_payload, fixed_event_id):
    return make_msg(event_id=fixed_event_id, payload=config_missing_payload)
