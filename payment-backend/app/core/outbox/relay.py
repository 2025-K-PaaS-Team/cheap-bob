"""OutboxRelay — main-backend 의 동일 모듈 미러.

outbox_event 폴링 → Kafka 발행 → published_at 마킹. At-least-once.
"""
from uuid import UUID
import json
from decimal import Decimal
from datetime import datetime
import asyncio

from app.database.session import UnitOfWork
from app.core.outbox.repository import OutboxEventRepository
from app.core.logger import get_logger
from app.core.kafka.producer import KafkaProducer
from app.config.setting import settings


logger = get_logger("outbox.relay")


def _json_default(value):
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, UUID):
        return str(value)
    if isinstance(value, datetime):
        return value.isoformat()
    raise TypeError(f"JSON 직렬화 불가 타입: {type(value)}")


class OutboxRelay:

    def __init__(self, uow: UnitOfWork, producer: KafkaProducer):
        self.uow = uow
        self.producer = producer
        self._stop_event = asyncio.Event()


    def request_stop(self) -> None:
        self._stop_event.set()


    async def run(self) -> None:
        if not settings.OUTBOX_RELAY_ENABLED:
            logger.info("OUTBOX_RELAY_ENABLED=false — relay 비활성, 루프 진입 안 함")
            return

        logger.info(
            "OutboxRelay 시작 — batch={}, poll={}ms, idle={}ms",
            settings.OUTBOX_RELAY_BATCH_SIZE,
            settings.OUTBOX_RELAY_POLL_INTERVAL_MS,
            settings.OUTBOX_RELAY_IDLE_BACKOFF_MS,
        )
        try:
            while not self._stop_event.is_set():
                try:
                    published = await self._tick()
                except Exception:
                    logger.exception("OutboxRelay tick 실패 — 다음 주기에 재시도")
                    published = 0

                delay_ms = (
                    settings.OUTBOX_RELAY_POLL_INTERVAL_MS
                    if published
                    else settings.OUTBOX_RELAY_IDLE_BACKOFF_MS
                )
                try:
                    await asyncio.wait_for(
                        self._stop_event.wait(), timeout=delay_ms / 1000,
                    )
                except asyncio.TimeoutError:
                    pass
        finally:
            logger.info("OutboxRelay 종료")


    async def _tick(self) -> int:
        async with self.uow as session:
            repo = OutboxEventRepository(session)
            events = await repo.claim_unpublished(limit=settings.OUTBOX_RELAY_BATCH_SIZE)
            if not events:
                return 0

            published_ids: list[int] = []
            for ev in events:
                try:
                    await self._publish(ev)
                except Exception:
                    logger.exception(
                        "outbox 발행 실패 event_id={} topic={} — 다음 tick 재시도",
                        ev.event_id, ev.topic,
                    )
                    raise
                published_ids.append(ev.id)

            await repo.mark_published(published_ids)
            logger.info("outbox 발행 완료 count={}", len(published_ids))
            return len(published_ids)


    async def _publish(self, event) -> None:
        headers = [
            ("event_id", str(event.event_id).encode("utf-8")),
            ("event_type", event.event_type.encode("utf-8")),
        ]
        for k, v in (event.headers or {}).items():
            headers.append((k, str(v).encode("utf-8")))

        await self.producer.raw.send_and_wait(
            topic=event.topic,
            key=event.aggregate_id.encode("utf-8"),
            value=json.dumps(event.payload, default=_json_default).encode("utf-8"),
            headers=headers,
        )
