"""Outbox enqueue 헬퍼.

도메인 서비스는 이 함수만 호출하면 된다 — Kafka 도 Relay 도 알 필요 없다.
`@transactional` 안에서 `self._session` 을 그대로 넘기면 비즈니스 데이터 INSERT 와
같은 트랜잭션에 자동 참여한다.

사용 예:
    @transactional
    async def withdraw_seller(self, email):
        await self._store_repo.delete(...)
        await enqueue_event(
            self._session,
            aggregate_type="Seller",
            aggregate_id=email,
            event_type="SellerStoreWithdrawn",
            topic="seller.store.withdrawn",
            payload={"store_id": store_id, "seller_email": email},
        )
        # @transactional 종료 시 commit — 비즈니스 + outbox 가 함께 영속화.
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
    """현재 트랜잭션에 outbox 이벤트를 추가한다.

    주의: 본 함수는 commit/flush 를 호출하지 않는다. 트랜잭션 경계는 caller (보통 `@transactional` 데코레이터) 가 소유.
    비즈니스 데이터 변경과 함께 영속화되어야 outbox 패턴이 성립한다.
    """
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
