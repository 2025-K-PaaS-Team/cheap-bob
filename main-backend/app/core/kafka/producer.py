"""Kafka producer 래퍼.

OutboxRelay 가 본 producer 를 사용해 발행. 다른 코드가 직접 producer 를 호출할 일은 없다 —
모든 도메인 이벤트는 enqueue_event 로 outbox 를 거치는 것이 원칙.

설정:
  - acks="all": 모든 in-sync 레플리카 ack 후 응답 (가장 강한 내구성)
  - enable_idempotence=True: 브로커 레벨 중복 차단 (재전송 시)
  - linger_ms=20: 작은 배치라도 잠깐 모아서 throughput 개선

lifecycle 은 container singleton 으로 관리 — main.py lifespan 에서 start/stop.
"""
from aiokafka import AIOKafkaProducer

from app.core.logger import get_logger
from app.config.setting import settings


logger = get_logger("kafka.producer")


class KafkaProducer:
    """단일 AIOKafkaProducer 의 lifespan 래퍼. Singleton 으로 주입."""

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
        """OutboxRelay 가 send_and_wait 호출 시 사용. start() 이후에만 호출."""
        if self._producer is None:
            raise RuntimeError("KafkaProducer 가 start 되지 않았습니다")
        return self._producer
