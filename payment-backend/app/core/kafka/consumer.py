"""Kafka consumer 베이스 — main-backend 의 동일 모듈 미러.

각 도메인의 `app/domain/<...>/event/<handler>.py` 가 본 베이스를 사용해 자기 토픽을 구독.

- manual offset commit — 핸들러 성공 후에만 커밋.
- dedupe 는 핸들러 안에서 ProcessedEventRepository.try_mark 로.
- 핸들러는 자기 트랜잭션 경계를 소유.
"""
from typing import Awaitable, Callable
import json
import asyncio
from aiokafka import AIOKafkaConsumer, ConsumerRecord

from app.core.logger import get_logger
from app.config.setting import settings


logger = get_logger("kafka.consumer")


EventHandler = Callable[[ConsumerRecord], Awaitable[None]]


class KafkaConsumerRunner:

    def __init__(self, *, group_id: str | None = None) -> None:
        self._handlers: dict[str, EventHandler] = {}
        self._group_id = group_id or settings.KAFKA_CONSUMER_GROUP
        self._stop_event = asyncio.Event()
        self._consumer: AIOKafkaConsumer | None = None


    def register(self, topic: str, handler: EventHandler) -> None:
        if topic in self._handlers:
            raise ValueError(f"topic={topic} 의 handler 가 이미 등록됨")
        self._handlers[topic] = handler


    def topics(self) -> list[str]:
        return list(self._handlers.keys())


    def request_stop(self) -> None:
        self._stop_event.set()


    async def run(self) -> None:
        topics = self.topics()
        if not topics:
            logger.info("KafkaConsumerRunner — 등록된 핸들러 없음, 컨슈머 시작 안 함")
            return

        self._consumer = AIOKafkaConsumer(
            *topics,
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            client_id=settings.KAFKA_CLIENT_ID,
            group_id=self._group_id,
            enable_auto_commit=False,
            auto_offset_reset="earliest",
            value_deserializer=lambda v: json.loads(v.decode("utf-8")) if v else None,
        )
        await self._consumer.start()
        logger.info(
            "Kafka consumer 시작 — group_id={} topics={}",
            self._group_id, topics,
        )
        try:
            while not self._stop_event.is_set():
                batch = await self._consumer.getmany(timeout_ms=500, max_records=50)
                for tp, messages in batch.items():
                    handler = self._handlers.get(tp.topic)
                    if handler is None:
                        logger.warning("핸들러 없는 토픽 메시지 수신 topic={}", tp.topic)
                        continue

                    last_committable: int | None = None
                    for msg in messages:
                        try:
                            await handler(msg)
                        except Exception:
                            logger.exception(
                                "이벤트 처리 실패 topic={} offset={} — commit 보류",
                                tp.topic, msg.offset,
                            )
                            last_committable = None
                            break
                        last_committable = msg.offset

                    if last_committable is not None:
                        await self._consumer.commit({tp: last_committable + 1})
        finally:
            await self._consumer.stop()
            self._consumer = None
            logger.info("Kafka consumer 종료")
