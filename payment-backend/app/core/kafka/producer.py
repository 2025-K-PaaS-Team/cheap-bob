"""Kafka producer 래퍼 — main-backend 의 동일 모듈 미러.

OutboxRelay 가 본 producer 를 사용해 발행. 모든 도메인 이벤트는 enqueue_event 로 outbox 를
거치는 것이 원칙.

설정: acks=all, enable_idempotence=True, linger_ms=20.
"""
from aiokafka import AIOKafkaProducer

from app.core.logger import get_logger
from app.config.setting import settings


logger = get_logger("kafka.producer")


class KafkaProducer:

    def __init__(self) -> None:
        self._producer: AIOKafkaProducer | None = None


    async def start(self) -> None:
        if self._producer is not None:
            return
        self._producer = AIOKafkaProducer(
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            client_id=settings.KAFKA_CLIENT_ID,
            acks="all",
            enable_idempotence=True,
            linger_ms=20,
            max_batch_size=16384,
        )
        await self._producer.start()
        logger.info(
            "Kafka producer 시작 — bootstrap={}, client_id={}",
            settings.KAFKA_BOOTSTRAP_SERVERS, settings.KAFKA_CLIENT_ID,
        )


    async def stop(self) -> None:
        if self._producer is None:
            return
        await self._producer.stop()
        self._producer = None
        logger.info("Kafka producer 종료")


    @property
    def raw(self) -> AIOKafkaProducer:
        if self._producer is None:
            raise RuntimeError("KafkaProducer 가 start 되지 않았습니다")
        return self._producer
