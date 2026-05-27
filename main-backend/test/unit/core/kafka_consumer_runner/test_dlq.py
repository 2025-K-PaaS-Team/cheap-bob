"""KafkaConsumerRunner DLQ 동작 단위 테스트.

`_dispatch` 가 외부 의존 (Kafka consumer/producer) 없이 검증 가능한 메서드라 별도로 테스트.
`run()` 전체는 통합 테스트 영역 (실 Kafka 필요).

핵심 시나리오:
  - terminal 실패 → 즉시 DLQ + commit
  - 일반 실패 < max_attempts → retry (no DLQ, no commit)
  - 일반 실패 >= max_attempts → DLQ + commit
  - 성공 → counter 정리 + commit
  - DLQ 발행 실패 → retry (commit 보류)
  - 같은 (topic, partition, event_id) 의 retry counter 누적
"""
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock
import pytest

from app.core.kafka.consumer import (
    KafkaConsumerRunner,
    TerminalEventError,
)


# ───────── helpers ─────────


def _msg(*, event_id: str = "11111111-1111-1111-1111-111111111111", offset: int = 1):
    """ConsumerRecord 의 최소 모양 — handler/_dispatch 가 쓰는 속성만."""
    headers = []
    if event_id is not None:
        headers.append(("event_id", event_id.encode("utf-8")))
    return SimpleNamespace(
        headers=headers,
        value={"k": "v"},
        offset=offset,
        key=b"agg_id",
        partition=0,
    )


def _tp(topic: str = "test.topic"):
    return SimpleNamespace(topic=topic, partition=0)


@pytest.fixture
def producer():
    """KafkaProducer mock — .raw.send_and_wait 만 stubbing."""
    raw = AsyncMock()
    raw.send_and_wait = AsyncMock()
    p = MagicMock()
    # raw 는 property — MagicMock 의 default 가 또 MagicMock 이라 raw.send_and_wait 가
    # AsyncMock 이어야 함.
    p.raw = raw
    return p


@pytest.fixture
def runner(producer):
    return KafkaConsumerRunner(producer=producer, group_id="test-group")


# ───────── tests ─────────


@pytest.mark.unit
class TestTerminalImmediateDLQ:

    async def test_terminal_error_sends_to_dlq_and_commits(
        self, runner, producer, monkeypatch,
    ):
        async def handler(_msg):
            raise TerminalEventError("schema fail")

        tp = _tp("seller.store.withdrawn")
        msg = _msg()

        outcome = await runner._dispatch(tp, msg, handler)

        assert outcome == "commit"
        # DLQ 발행.
        producer.raw.send_and_wait.assert_awaited_once()
        call = producer.raw.send_and_wait.await_args
        assert call.kwargs["topic"] == "seller.store.withdrawn.dlq"
        headers = dict(call.kwargs["headers"])
        assert headers["x-original-topic"] == b"seller.store.withdrawn"
        assert headers["x-failure-reason"].startswith(b"schema fail")
        assert headers["x-attempt-count"] == b"1"
        # counter 정리.
        assert not runner._attempt_counts


@pytest.mark.unit
class TestRetryThenDLQ:

    async def test_under_max_attempts_returns_retry(
        self, runner, producer, monkeypatch,
    ):
        # CONSUMER_MAX_ATTEMPTS=5 (default). 실패 1회는 retry.
        async def handler(_msg):
            raise RuntimeError("transient")

        tp = _tp()
        msg = _msg()
        outcome = await runner._dispatch(tp, msg, handler)

        assert outcome == "retry"
        producer.raw.send_and_wait.assert_not_awaited()
        assert runner._attempt_counts[(tp.topic, tp.partition, _key_event(msg))] == 1


    async def test_at_max_attempts_dlq_and_commit(
        self, runner, producer, monkeypatch,
    ):
        # max_attempts=3 으로 단축.
        monkeypatch.setattr(
            "app.core.kafka.consumer.settings.CONSUMER_MAX_ATTEMPTS", 3,
        )

        async def handler(_msg):
            raise RuntimeError("transient")

        tp = _tp()
        msg = _msg()
        # 1, 2 — retry.
        await runner._dispatch(tp, msg, handler)
        await runner._dispatch(tp, msg, handler)
        producer.raw.send_and_wait.assert_not_awaited()
        # 3 — DLQ + commit.
        outcome = await runner._dispatch(tp, msg, handler)

        assert outcome == "commit"
        producer.raw.send_and_wait.assert_awaited_once()
        headers = dict(producer.raw.send_and_wait.await_args.kwargs["headers"])
        assert headers["x-attempt-count"] == b"3"
        # counter 정리.
        assert not runner._attempt_counts


@pytest.mark.unit
class TestSuccessClearsCounter:

    async def test_success_after_failures_resets_counter(
        self, runner, producer,
    ):
        calls = {"n": 0}
        async def handler(_msg):
            calls["n"] += 1
            if calls["n"] < 2:
                raise RuntimeError("first fails")

        tp = _tp()
        msg = _msg()
        # 첫 호출 실패 — retry, counter=1.
        await runner._dispatch(tp, msg, handler)
        assert runner._attempt_counts[(tp.topic, tp.partition, _key_event(msg))] == 1
        # 두 번째 성공.
        outcome = await runner._dispatch(tp, msg, handler)
        assert outcome == "commit"
        assert not runner._attempt_counts
        producer.raw.send_and_wait.assert_not_awaited()


@pytest.mark.unit
class TestDLQPublishFails:
    """DLQ 발행 자체가 실패하면 commit 보류 — 원본도 재배달."""

    async def test_dlq_send_failure_returns_retry(
        self, runner, producer, monkeypatch,
    ):
        producer.raw.send_and_wait.side_effect = RuntimeError("kafka down")

        async def handler(_msg):
            raise TerminalEventError("schema fail")

        outcome = await runner._dispatch(_tp(), _msg(), handler)

        assert outcome == "retry"
        # counter 정리 안 됨 — 다음 시도 시 attempts=1 유지.
        assert runner._attempt_counts == {}  # terminal 은 counter 사용 안 함, 정리 시도만.


@pytest.mark.unit
class TestPerEventCounter:

    async def test_different_event_ids_track_independently(
        self, runner, producer,
    ):
        async def handler(_msg):
            raise RuntimeError("boom")

        tp = _tp()
        msg_a = _msg(event_id="aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa", offset=1)
        msg_b = _msg(event_id="bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb", offset=2)

        await runner._dispatch(tp, msg_a, handler)
        await runner._dispatch(tp, msg_b, handler)
        await runner._dispatch(tp, msg_a, handler)

        assert runner._attempt_counts[(tp.topic, tp.partition, _key_event(msg_a))] == 2
        assert runner._attempt_counts[(tp.topic, tp.partition, _key_event(msg_b))] == 1


# ───────── private helpers ─────────


def _key_event(msg) -> str:
    """테스트용 — handler 가 보는 event_id 헤더."""
    headers = {k: v.decode("utf-8") for k, v in (msg.headers or [])}
    return headers.get("event_id") or f"_off{msg.offset}"
