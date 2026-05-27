"""payment.refund.failed 이벤트 핸들러 — main-backend (consumer) 측.

PortOne 4xx (이미 취소 / 거부) 또는 가게 결제 설정 누락 등 **자동 회복 불가** 한 실패 신호.
주문 상태는 그대로 (reservation/accept) 두고, CRITICAL 로깅으로 운영자 알람만 트리거.

운영 후속:
  - 알람 받은 운영자가 PortOne 콘솔에서 진위 확인.
  - 실제 환불됐다면 DB 를 수동 cancel 처리.
  - 가게 결제 설정 누락이라면 seller 에게 안내.

ProcessedEvent dedupe 는 적용 — 같은 failure 이벤트의 재배달이 알람을 2번 울리지 않게.
"""
from uuid import UUID
from pydantic import ValidationError
from aiokafka import ConsumerRecord

from app.domain.order.event.refund import (
    TOPIC_PAYMENT_REFUND_FAILED,
    PaymentRefundFailedPayload,
)
from app.database.session import UnitOfWork, transactional
from app.core.outbox.repository import ProcessedEventRepository
from app.core.logger import get_logger


logger = get_logger("event.refund_failed")


class PaymentRefundFailedEventHandler:

    def __init__(self, uow: UnitOfWork):
        self.uow = uow


    async def handle(self, msg: ConsumerRecord) -> None:
        event_id = _extract_event_id(msg)
        try:
            payload = PaymentRefundFailedPayload.model_validate(msg.value)
        except ValidationError:
            logger.exception(
                "[CRITICAL] failed payload 검증 실패 skip event_id={} value={}",
                event_id, msg.value,
            )
            return

        await self._record(event_id=event_id, payload=payload)


    @transactional
    async def _record(
        self, *, event_id: UUID, payload: PaymentRefundFailedPayload,
    ) -> None:
        is_new = await ProcessedEventRepository(self._session).try_mark(
            event_id=event_id, topic=TOPIC_PAYMENT_REFUND_FAILED,
        )
        if not is_new:
            logger.info(
                "중복 failure 이벤트 skip event_id={} payment_id={}",
                event_id, payload.payment_id,
            )
            return

        logger.error(
            "[CRITICAL] 환불 실패 — 운영자 보정 필요 "
            "payment_id={} store_id={} kind={} detail={}",
            payload.payment_id, payload.store_id,
            payload.error_kind, payload.error_detail,
        )


def _extract_event_id(msg: ConsumerRecord) -> UUID:
    headers = {k: v.decode("utf-8") for k, v in (msg.headers or [])}
    raw = headers.get("event_id")
    if raw is None:
        raise ValueError(f"event_id 헤더 누락 offset={msg.offset}")
    return UUID(raw)
