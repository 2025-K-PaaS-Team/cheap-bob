"""Outbox enqueue 헬퍼 — main-backend 의 동일 모듈 미러.

도메인 서비스는 본 함수만 호출. Kafka 호출/Relay 동작을 알 필요 없다.
`@transactional` 안에서 `self._session` 을 그대로 넘기면 비즈니스 데이터 INSERT 와 같은
트랜잭션에 자동 참여한다.
"""
from uuid import UUID, uuid4
from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.outbox.model import OutboxEvent


async def enqueue_event(
    session: AsyncSession,
    *,
    aggregate_type: str,
    aggregate_id: str,
    event_type: str,
    topic: str,
    payload: dict[str, Any],
    headers: dict[str, Any] | None = None,
    event_id: UUID | None = None,
) -> OutboxEvent:
    """현재 트랜잭션에 outbox 이벤트를 추가한다. commit 은 호출 측 책임."""
    event = OutboxEvent(
        event_id=event_id or uuid4(),
        aggregate_type=aggregate_type,
        aggregate_id=str(aggregate_id),
        event_type=event_type,
        topic=topic,
        payload=payload,
        headers=headers or {},
    )
    session.add(event)
    return event
