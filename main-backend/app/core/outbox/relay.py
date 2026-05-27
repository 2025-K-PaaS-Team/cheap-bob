"""OutboxRelay — outbox_event 폴링 → Kafka 발행 → published_at 마킹.

lifespan 에서 백그라운드 태스크로 띄운다. 다중 인스턴스 안전 (SKIP LOCKED).

신뢰성 보장:
  - At-least-once 발행. send_and_wait 직후 DB 커밋 직전에 죽으면 같은 행을 다음 폴링에서
    다시 잡고 재발행. 컨슈머가 event_id 로 중복 차단해야 한다 (ProcessedEvent).
  - SELECT ... FOR UPDATE SKIP LOCKED — 여러 인스턴스가 같은 행을 잡지 않음.
  - 같은 aggregate_id 의 이벤트는 같은 Kafka 파티션 (메시지 key 로 사용) — 순서 보장.

설계 메모: producer 는 `KafkaProducer` Singleton 주입 — Relay 가 producer lifecycle 을
소유하지 않는다. lifespan 에서 producer.start() → relay.run() → relay.stop() → producer.stop()
순서.
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
    """JSONB payload 직렬화 보조 — Decimal/UUID/datetime 을 문자열화."""
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, UUID):
        return str(value)
    if isinstance(value, datetime):
        return value.isoformat()
    raise TypeError(f"JSON 직렬화 불가 타입: {type(value)}")


class OutboxRelay:
    """outbox_event → Kafka 폴링 발행 루프.

    main.py lifespan 이 `asyncio.create_task(relay.run())` 로 띄우고, 종료 시
    `request_stop()` → `await task` 로 정상 종료.
    """

    def __init__(self, uow: UnitOfWork, producer: KafkaProducer):
        self.uow = uow
        self.producer = producer
        self._stop_event = asyncio.Event()


    def request_stop(self) -> None:
        self._stop_event.set()


    async def run(self) -> None:
        """폴링 루프. ENABLED=false 면 즉시 종료."""
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

                # 일이 있으면 빠른 다음 폴, 없으면 idle backoff — DB 부하 절감.
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
        """한 번의 폴링. claim → send_and_wait → mark_published 를 한 트랜잭션에서.

        Returns: 발행 건수.
        """
        async with self.uow as session:
            repo = OutboxEventRepository(session)
            events = await repo.claim_unpublished(limit=settings.OUTBOX_RELAY_BATCH_SIZE)
            if not events:
                # 빈 트랜잭션은 commit/rollback 양쪽 다 안전 — UoW 가 commit 처리.
                return 0

            published_ids: list[int] = []
            for ev in events:
                try:
                    await self._publish(ev)
                except Exception:
                    # 단일 행 발행 실패 — 트랜잭션 전체 rollback 으로 모두 미발행 상태 유지.
                    # 다음 tick 에서 재시도.
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
        """단건 발행 — event_id/event_type 을 Kafka 헤더에 명시.

        헤더가 있으면 consumer 가 payload 파싱 전에 dedupe/routing 결정 가능.
        """
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
