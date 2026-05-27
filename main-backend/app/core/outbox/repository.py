"""Outbox / ProcessedEvent 의 repository.

도메인 repository 들과 동일 컨벤션 — 세션을 생성자로 받아 메서드별 쿼리만 책임.
"""
from uuid import UUID
from typing import Any, Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy import select, update
from datetime import datetime, timezone

from app.core.outbox.model import OutboxEvent, ProcessedEvent


class OutboxEventRepository:
    """발행 큐 — Relay 가 사용. enqueue 는 별도 헬퍼 `enqueue_event` 참조."""

    def __init__(self, session: AsyncSession):
        self.session = session


    async def claim_unpublished(
        self, *, limit: int,
    ) -> Sequence[OutboxEvent]:
        """미발행 행을 잠가서 가져온다.

        SKIP LOCKED — 다른 인스턴스의 Relay 가 잡고 있는 행은 건너뛴다 (다중 인스턴스
        안전). `with_for_update(skip_locked=True)` 의 트랜잭션은 호출 측이 소유한다.
        """
        stmt = (
            select(OutboxEvent)
            .where(OutboxEvent.published_at.is_(None))
            .order_by(OutboxEvent.id)
            .with_for_update(skip_locked=True)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()


    async def mark_published(self, ids: Sequence[int]) -> None:
        """발행 완료 마킹. 호출 측이 claim 과 같은 트랜잭션 안에서 호출."""
        if not ids:
            return
        await self.session.execute(
            update(OutboxEvent)
            .where(OutboxEvent.id.in_(list(ids)))
            .values(published_at=datetime.now(timezone.utc)),
        )


    async def oldest_unpublished_age_seconds(self) -> float | None:
        """모니터링 용 — 가장 오래된 미발행 이벤트의 age 초. 없으면 None.

        Relay lag 알람의 입력으로 사용 (예: 60초 초과 시 경보).
        """
        stmt = (
            select(OutboxEvent.created_at)
            .where(OutboxEvent.published_at.is_(None))
            .order_by(OutboxEvent.id)
            .limit(1)
        )
        result = await self.session.execute(stmt)
        oldest = result.scalar_one_or_none()
        if oldest is None:
            return None
        return (datetime.now(timezone.utc) - oldest).total_seconds()


class ProcessedEventRepository:
    """consumer 멱등성 ledger."""

    def __init__(self, session: AsyncSession):
        self.session = session


    async def try_mark(
        self, *, event_id: UUID, topic: str,
    ) -> bool:
        """이벤트가 처음이면 True (=처리 진행), 중복이면 False (=skip).

        `stock_operation_log.try_insert` 와 같은 패턴 — PK 충돌을 INSERT ... ON
        CONFLICT DO NOTHING 으로 흡수.
        """
        stmt = (
            pg_insert(ProcessedEvent)
            .values(event_id=event_id, topic=topic)
            .on_conflict_do_nothing(index_elements=[ProcessedEvent.event_id])
            .returning(ProcessedEvent.event_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None
