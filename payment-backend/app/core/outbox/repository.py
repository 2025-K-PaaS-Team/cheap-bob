"""Outbox / ProcessedEvent 의 repository — main-backend 의 동일 모듈 미러."""
from uuid import UUID
from typing import Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy import select, update
from datetime import datetime, timezone

from app.core.outbox.model import OutboxEvent, ProcessedEvent


class OutboxEventRepository:

    def __init__(self, session: AsyncSession):
        self.session = session


    async def claim_unpublished(
        self, *, limit: int,
    ) -> Sequence[OutboxEvent]:
        """SKIP LOCKED — 다른 Relay 인스턴스가 잡은 행은 건너뛴다."""
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
        if not ids:
            return
        await self.session.execute(
            update(OutboxEvent)
            .where(OutboxEvent.id.in_(list(ids)))
            .values(published_at=datetime.now(timezone.utc)),
        )


    async def oldest_unpublished_age_seconds(self) -> float | None:
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

    def __init__(self, session: AsyncSession):
        self.session = session


    async def try_mark(
        self, *, event_id: UUID, topic: str,
    ) -> bool:
        """이벤트가 처음이면 True, 중복이면 False."""
        stmt = (
            pg_insert(ProcessedEvent)
            .values(event_id=event_id, topic=topic)
            .on_conflict_do_nothing(index_elements=[ProcessedEvent.event_id])
            .returning(ProcessedEvent.event_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None
