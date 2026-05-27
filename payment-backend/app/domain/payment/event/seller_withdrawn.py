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
  - 메시지 파싱 실패 (event_id 누락 / payload schema 위배) → TerminalEventError →
    Runner 가 즉시 `<topic>.dlq` 로 격리 + offset 전진. 운영자가 DLQ 검사.
  - delete_by_store 가 DB 오류 raise → tx rollback (try_mark 도 무효) → 재배달 → 결국 max_attempts 도달 시 DLQ.
"""
from uuid import UUID
from pydantic import BaseModel, ValidationError
from aiokafka import ConsumerRecord

from app.domain.payment.service.store_payment_info import StorePaymentInfoService
from app.database.session import UnitOfWork, transactional
from app.core.outbox.repository import ProcessedEventRepository
from app.core.logger import get_logger
from app.core.kafka.consumer import TerminalEventError, extract_event_id_header


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
        """Kafka 메시지 1건 처리. raise 하면 Runner 가 retry/DLQ 분기."""
        event_id = extract_event_id_header(msg)
        try:
            payload = SellerStoreWithdrawnPayload.model_validate(msg.value)
        except ValidationError as e:
            # schema 위배 — retry 무의미. DLQ 로 격리 (Runner 가 처리).
            raise TerminalEventError(
                f"payload 검증 실패 event_id={event_id}: {e}",
            ) from e

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
