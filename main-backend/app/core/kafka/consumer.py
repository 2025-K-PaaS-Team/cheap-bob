"""Kafka consumer 베이스 — 도메인별 핸들러 어댑터.

각 도메인의 `app/domain/<...>/event/<handler>.py` 가 본 베이스를 사용해 자기 토픽을 구독.
하나의 컨슈머 프로세스 안에서 여러 토픽/핸들러를 다중화하고, 핸들러 함수에 멱등성 키
(event_id) dedupe 를 끼워 넣는다.

설계 포인트:
  - manual offset commit — 핸들러 성공 후에만 커밋. 핸들러 실패 시 같은 메시지를 다음에
    다시 받는다. enable_auto_commit=False.
  - dedupe 는 핸들러 안에서 ProcessedEventRepository.try_mark 로. 핸들러는 try_mark 가
    False (=중복) 면 즉시 return — 비즈니스 로직을 두 번 실행하지 않는다.
  - 핸들러는 자기 트랜잭션 경계를 소유. 본 베이스는 비즈니스 로직을 모른다.
"""
from typing import Awaitable, Callable
import json
import asyncio
from aiokafka import AIOKafkaConsumer, ConsumerRecord

from app.core.logger import get_logger
from app.config.setting import settings


logger = get_logger("kafka.consumer")


# 핸들러 시그니처 — 메시지 1건을 받아 처리한다. 예외 raise 시 offset 커밋되지 않음.
EventHandler = Callable[[ConsumerRecord], Awaitable[None]]


class KafkaConsumerRunner:
    """단일 컨슈머 프로세스. 토픽 → 핸들러 매핑 dispatch.

    사용 예:
        runner = KafkaConsumerRunner(group_id=...)
        runner.register("seller.store.withdrawn", handle_seller_withdrawn)
        await runner.run()
    """

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
        """모든 등록된 토픽을 한 컨슈머로 구독.

        멱등성/dedupe 는 핸들러 책임이며, 본 runner 는 raise 발생 시 commit 을 보류하고
        같은 메시지가 재배달되도록 둔다 (at-least-once).
        """
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
                        # subscribe 후 register 가 빠진 토픽 — defensive log.
                        logger.warning("핸들러 없는 토픽 메시지 수신 topic={}", tp.topic)
                        continue

                    last_committable: int | None = None
                    for msg in messages:
                        try:
                            await handler(msg)
                        except Exception:
                            # 본 메시지 실패 — 같은 파티션의 이후 메시지를 처리하지 않고
                            # offset commit 도 보류. 다음 poll 에서 다시 시작.
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
