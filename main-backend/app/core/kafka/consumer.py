"""Kafka consumer 베이스 — 도메인별 핸들러 어댑터 + DLQ.

각 도메인의 `app/domain/<...>/event/<handler>.py` 가 본 베이스를 사용해 자기 토픽을 구독.
하나의 컨슈머 프로세스 안에서 여러 토픽/핸들러를 다중화한다.

설계 포인트:
  - manual offset commit — 핸들러 성공 또는 DLQ 이동 후에만 커밋.
  - dedupe 는 핸들러 안에서 ProcessedEventRepository.try_mark 로. 핸들러는 try_mark 가
    False (=중복) 면 즉시 return — 비즈니스 로직을 두 번 실행하지 않는다.
  - 핸들러는 자기 트랜잭션 경계를 소유. 본 베이스는 비즈니스 로직을 모른다.

DLQ (Dead Letter Queue):
  - 핸들러가 `TerminalEventError` raise → **즉시** `<topic>.dlq` 로 격리 + offset 전진.
  - 일반 Exception → in-memory retry counter +1. CONSUMER_MAX_ATTEMPTS 도달 시 DLQ.
  - 미달이면 `last_committable=None; break` 로 다음 poll 에 재배달 (기존 동작 보존).
  - DLQ 메시지 자체 발행이 실패하면 commit 보류 — 원본도 재배달 (안전).
  retry counter 는 프로세스 메모리에 보관 — 재시작 시 reset (acceptable: 재시작 후
  무한 retry 가 다시 시작되어도 결국 DLQ 로 갈 것).
"""
from uuid import UUID
from typing import Awaitable, Callable
import json
import asyncio
from aiokafka import AIOKafkaConsumer, ConsumerRecord, TopicPartition

from app.core.kafka.producer import KafkaProducer
from app.core.logger import get_logger
from app.config.setting import settings


logger = get_logger("kafka.consumer")


# 핸들러 시그니처 — 메시지 1건을 받아 처리. 예외 raise 시 retry/DLQ 분기.
EventHandler = Callable[[ConsumerRecord], Awaitable[None]]


class TerminalEventError(Exception):
    """retry 가 결과를 바꾸지 못하는 영구 실패 — schema 검증 실패, 필수 헤더 누락 등.

    consumer 가 본 예외를 catch 하면 **즉시 DLQ** 로 보내고 offset 을 전진시킨다.
    transient 실패 (DB/네트워크 일시 장애) 는 일반 Exception 으로 raise — retry counter 가 적용된다.
    """


def extract_event_id_header(msg: ConsumerRecord) -> UUID:
    """공통 헬퍼 — outbox-relay 발행 메시지의 event_id 헤더 추출.

    Relay 가 항상 채우므로 누락은 outbox 우회 produce 또는 schema 사고. terminal 처리.
    """
    headers = {k: v.decode("utf-8") for k, v in (msg.headers or [])}
    raw = headers.get("event_id")
    if raw is None:
        raise TerminalEventError(f"event_id 헤더 누락 offset={msg.offset}")
    try:
        return UUID(raw)
    except ValueError as e:
        raise TerminalEventError(f"event_id 가 UUID 가 아님 raw={raw!r}") from e


class KafkaConsumerRunner:
    """단일 컨슈머 프로세스. 토픽 → 핸들러 매핑 + DLQ 격리.

    사용 예:
        runner = KafkaConsumerRunner(producer=kafka_producer)
        runner.register("seller.store.withdrawn", handle_seller_withdrawn)
        await runner.run()
    """

    def __init__(
        self,
        *,
        producer: KafkaProducer,
        group_id: str | None = None,
    ) -> None:
        self._handlers: dict[str, EventHandler] = {}
        self._group_id = group_id or settings.KAFKA_CONSUMER_GROUP
        self._stop_event = asyncio.Event()
        self._consumer: AIOKafkaConsumer | None = None
        # DLQ 발행용 — Relay 와 같은 producer Singleton 공유.
        self._producer = producer
        # (topic, partition, event_id) → 연속 실패 횟수. 재시작 시 reset.
        self._attempt_counts: dict[tuple[str, int, str], int] = {}


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
            "Kafka consumer 시작 — group_id={} topics={} max_attempts={}",
            self._group_id, topics, settings.CONSUMER_MAX_ATTEMPTS,
        )
        try:
            while not self._stop_event.is_set():
                batch = await self._consumer.getmany(timeout_ms=500, max_records=50)
                for tp, messages in batch.items():
                    handler = self._handlers.get(tp.topic)
                    if handler is None:
                        logger.warning("핸들러 없는 토픽 메시지 수신 topic={}", tp.topic)
                        continue

                    last_committable = await self._process_partition(
                        tp, messages, handler,
                    )
                    if last_committable is not None:
                        await self._consumer.commit({tp: last_committable + 1})
        finally:
            await self._consumer.stop()
            self._consumer = None
            logger.info("Kafka consumer 종료")


    # ───────── private ─────────


    async def _process_partition(
        self,
        tp: TopicPartition,
        messages: list[ConsumerRecord],
        handler: EventHandler,
    ) -> int | None:
        """파티션 1개 분 batch 처리. Returns 마지막 commitable offset (또는 None)."""
        last_committable: int | None = None
        for msg in messages:
            outcome = await self._dispatch(tp, msg, handler)
            if outcome == "retry":
                # 재배달 보류 — 이 메시지부터 다시. 이후 메시지는 다음 poll 에서.
                break
            # "commit" — 성공 / DLQ 이동 모두 offset 전진.
            last_committable = msg.offset
        return last_committable


    async def _dispatch(
        self, tp: TopicPartition, msg: ConsumerRecord, handler: EventHandler,
    ) -> str:
        """단건 dispatch. Returns 'commit' 또는 'retry'."""
        key = self._attempt_key(tp, msg)
        try:
            await handler(msg)
        except TerminalEventError as e:
            # 명시적 영구 실패 — retry 무의미. 즉시 DLQ.
            logger.warning(
                "terminal 실패 — DLQ 격리 topic={} offset={}: {}",
                tp.topic, msg.offset, e,
            )
            if await self._send_to_dlq(tp, msg, reason=str(e), attempts=1):
                self._attempt_counts.pop(key, None)
                return "commit"
            return "retry"
        except Exception as e:
            attempts = self._attempt_counts.get(key, 0) + 1
            self._attempt_counts[key] = attempts
            max_attempts = settings.CONSUMER_MAX_ATTEMPTS
            if max_attempts and attempts >= max_attempts:
                logger.error(
                    "max_attempts ({}) 초과 — DLQ 격리 topic={} offset={}: {}",
                    max_attempts, tp.topic, msg.offset, e,
                )
                if await self._send_to_dlq(
                    tp, msg, reason=str(e), attempts=attempts,
                ):
                    self._attempt_counts.pop(key, None)
                    return "commit"
                return "retry"

            logger.warning(
                "이벤트 처리 실패 {}/{} topic={} offset={}: {} — retry",
                attempts, max_attempts or "∞", tp.topic, msg.offset, e,
            )
            return "retry"
        else:
            self._attempt_counts.pop(key, None)
            return "commit"


    async def _send_to_dlq(
        self, tp: TopicPartition, msg: ConsumerRecord,
        *, reason: str, attempts: int,
    ) -> bool:
        """`<topic>.dlq` 로 메시지 + 메타데이터 발행. 실패 시 False (caller retry)."""
        dlq_topic = f"{tp.topic}.dlq"
        # 원본 헤더 보존 + 진단 메타데이터 추가.
        headers = [(k, v) for k, v in (msg.headers or [])]
        headers.extend([
            ("x-original-topic", tp.topic.encode("utf-8")),
            ("x-original-partition", str(tp.partition).encode("utf-8")),
            ("x-original-offset", str(msg.offset).encode("utf-8")),
            # reason 너무 길면 메시지 크기 폭주 방지. 천 자 컷.
            ("x-failure-reason", reason[:1000].encode("utf-8")),
            ("x-attempt-count", str(attempts).encode("utf-8")),
        ])
        # consumer 가 value_deserializer 로 dict 화 했으니 재직렬화.
        value_bytes = (
            json.dumps(msg.value).encode("utf-8") if msg.value is not None else None
        )
        try:
            await self._producer.raw.send_and_wait(
                topic=dlq_topic,
                key=msg.key,
                value=value_bytes,
                headers=headers,
            )
            return True
        except Exception:
            logger.exception(
                "[CRITICAL] DLQ 발행 실패 — 원본 메시지 재시도 대상 "
                "dlq_topic={} original_offset={}",
                dlq_topic, msg.offset,
            )
            return False


    def _attempt_key(
        self, tp: TopicPartition, msg: ConsumerRecord,
    ) -> tuple[str, int, str]:
        """retry counter key. event_id 없으면 offset 으로 fallback."""
        headers = {k: v.decode("utf-8") for k, v in (msg.headers or [])}
        event_id = headers.get("event_id") or f"_off{msg.offset}"
        return (tp.topic, tp.partition, event_id)
