from unittest.mock import MagicMock
from types import SimpleNamespace
import pytest

from test.unit.domain.payment.seller_withdrawn_event_handler.mock_factory import (
    FakeUnitOfWork,
    ProcessedEventRepoMockFactory,
    StorePaymentInfoServiceMockFactory,
    make_mock_session,
)

from app.domain.payment.event.seller_withdrawn import (
    SellerStoreWithdrawnEventHandler,
)


@pytest.fixture
def mock_session():
    return make_mock_session()


@pytest.fixture
def store_payment_info_mock():
    return StorePaymentInfoServiceMockFactory.create()


@pytest.fixture
def processed_event_repo_mock():
    return ProcessedEventRepoMockFactory.create()


@pytest.fixture
def mock_logger(monkeypatch):
    """loguru logger 를 MagicMock 으로 교체 — call args 검증 가능."""
    mock = MagicMock()
    monkeypatch.setattr(
        "app.domain.payment.event.seller_withdrawn.logger", mock,
    )
    return mock


@pytest.fixture
def handler(
    monkeypatch, mock_session,
    store_payment_info_mock, processed_event_repo_mock,
):
    monkeypatch.setattr(
        "app.domain.payment.event.seller_withdrawn.ProcessedEventRepository",
        lambda session: processed_event_repo_mock,
    )
    return SellerStoreWithdrawnEventHandler(
        uow=FakeUnitOfWork(mock_session),
        store_payment_info_service=store_payment_info_mock,
    )


# ───────── 메시지 빌더 ─────────


def _make_msg(*, event_id: str | None, payload):
    """ConsumerRecord 최소 모양. event_id=None 이면 헤더 자체 없음."""
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
def valid_payload():
    return {
        "store_id": "STR_test",
        "seller_email": "seller@example.com",
    }


@pytest.fixture
def msg(make_msg, valid_payload, fixed_event_id):
    return make_msg(event_id=fixed_event_id, payload=valid_payload)
