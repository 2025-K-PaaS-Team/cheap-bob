"""seller.store.withdrawn 이벤트 핸들러 — payment-backend (consumer) 측.

main-backend (producer) 의 `app.domain.seller.event.withdrawn` 와 1:1 미러.
shared 패턴 미적용 정책 — 양쪽이 같은 schema 를 자체 정의로 보유. 계약 변경 시 양쪽 동시 수정.

수신 흐름:
  1. KafkaConsumerRunner 가 토픽 메시지 수신.
  2. handler 가 헤더에서 event_id 추출.
  3. ProcessedEvent.try_mark(event_id) → False (=중복) 면 즉시 return.
  4. payload 파싱 후 store_payment_info_service.delete_by_store(store_id) 호출.
  5. ProcessedEvent INSERT 와 delete 가 같은 트랜잭션 — at-least-once 가 effectively-once.

실패 정책:
  - 메시지 파싱 실패 (event_id 누락 / payload 불량) → ValueError raise → Runner 가 offset
    commit 보류 → 같은 메시지 재배달. 데이터 자체가 깨졌으면 영원히 재시도되니, DLQ 도입 전에는 운영자가 토픽에서 manual offset advance 필요.
  - delete_by_store 가 DB 오류 raise → tx rollback (try_mark 도 무효) → 다음 배달에 재시도.
"""
from uuid import UUID
from pydantic import BaseModel, ValidationError
from aiokafka import ConsumerRecord

from app.domain.payment.service.store_payment_info import StorePaymentInfoService
from app.database.session import UnitOfWork, transactional
from app.core.outbox.repository import ProcessedEventRepository
from app.core.logger import get_logger


logger = get_logger("event.seller_withdrawn")


# main-backend 의 SellerStoreWithdrawnPayload 와 1:1 매칭.
class SellerStoreWithdrawnPayload(BaseModel):
    store_id: str
    seller_email: str


# Topic 상수 — 등록 시 사용. main-backend 와 동일 문자열.
TOPIC_SELLER_STORE_WITHDRAWN = "seller.store.withdrawn"


class SellerStoreWithdrawnEventHandler:
    """seller.store.withdrawn 메시지 1건 → store_payment_info 삭제.

    Service-shaped — Container 에서 Factory 로 생성. lifespan 이 인스턴스를 만들고 핸들러
    callable (`.handle`) 을 KafkaConsumerRunner.register 에 등록.
    """

    def __init__(
        self,
        uow: UnitOfWork,
        store_payment_info_service: StorePaymentInfoService,
    ):
        self.uow = uow
        self.store_payment_info_service = store_payment_info_service


    async def handle(self, msg: ConsumerRecord) -> None:
        """Kafka 메시지 1건 처리. raise 하면 Runner 가 offset commit 보류 (재배달)."""
        event_id = _extract_event_id(msg)
        try:
            payload = SellerStoreWithdrawnPayload.model_validate(msg.value)
        except ValidationError:
            # payload 가 schema 와 안 맞으면 처리 불가 — raise 하면 재배달 무한루프.
            # 본 케이스는 producer 측 버그/스키마 깨짐이므로 CRITICAL 로그만 남기고 skip.
            logger.exception(
                "[CRITICAL] payload 검증 실패 — skip event_id={} value={}",
                event_id, msg.value,
            )
            return

        await self._apply(event_id=event_id, payload=payload)


    @transactional
    async def _apply(
        self, *, event_id: UUID, payload: SellerStoreWithdrawnPayload,
    ) -> None:
        """한 트랜잭션에서 dedupe + delete. raise 시 둘 다 rollback."""
        is_new = await ProcessedEventRepository(self._session).try_mark(
            event_id=event_id, topic=TOPIC_SELLER_STORE_WITHDRAWN,
        )
        if not is_new:
            logger.info(
                "중복 이벤트 skip event_id={} store_id={}",
                event_id, payload.store_id,
            )
            return

        # delete_by_store 는 @transactional + ContextVar 로 같은 세션에 참여.
        deleted = await self.store_payment_info_service.delete_by_store(payload.store_id)
        logger.info(
            "SellerStoreWithdrawn 처리 store_id={} seller_email={} deleted={}",
            payload.store_id, payload.seller_email, deleted,
        )


def _extract_event_id(msg: ConsumerRecord) -> UUID:
    """헤더에서 event_id 추출 — Relay 가 항상 채워넣는다."""
    headers = {k: v.decode("utf-8") for k, v in (msg.headers or [])}
    raw = headers.get("event_id")
    if raw is None:
        # event_id 없는 메시지는 producer 가 outbox 가 아닌 직접 produce 한 케이스 — 비정상.
        raise ValueError(f"event_id 헤더 누락 offset={msg.offset}")
    return UUID(raw)
