"""order.refund.requested 이벤트 핸들러 — payment-backend (consumer + producer).

처리 흐름 (한 트랜잭션):
  1. ProcessedEvent.try_mark(event_id) — 중복이면 즉시 return.
  2. store_payment_info_service.get_complete_by_store(store_id) — secret_key 조회.
  3. payment_gateway_service.refund(payment_id, secret_key, reason) — PortOne 호출 (외부).
  4. 결과별 분기:
     - 성공            → enqueue payment.refund.completed (같은 tx 의 outbox).
     - PaymentRefundError (4xx 영구 실패) → enqueue payment.refund.failed (terminal).
     - PaymentInfoMissingError/Incomplete → enqueue payment.refund.failed (config 문제).
     - PaymentRefundTransientError (5xx/네트워크) → raise → consumer retry.
  5. commit — ProcessedEvent + outbox 가 함께 영속화. Relay 가 곧 Kafka 로 발행.

외부 호출 ↔ DB tx 의 race:
  - PortOne refund 가 성공한 직후 DB commit 이 실패한다면 ProcessedEvent INSERT 도 롤백.
  - 다음 배달에서 다시 try_mark — 통과 — PortOne 재호출 — **이미 취소된 결제** → 4xx.
  - 우리는 4xx 를 `PaymentRefundError` 로 받아 "이미 끝남" 으로 안전하게 failed 발행.
    (실제로는 환불 성공이지만 main-backend 가 보정해야 함 — TODO 알람용 시그널.)
  - PortOne 의 idempotency 가 단단하면 4xx 대신 "already cancelled" 의 다른 신호를 줄 수도.
    그 경우 본 핸들러는 약간 보수적 — 운영 모니터링 으로 patch 가능.
"""
from uuid import UUID
from pydantic import ValidationError
from aiokafka import ConsumerRecord

from app.domain.payment.service.store_payment_info import StorePaymentInfoService
from app.domain.payment.service.payment_gateway import PaymentGatewayService
from app.domain.payment.service.exception import (
    PaymentInfoIncompleteError,
    PaymentInfoMissingError,
    PaymentRefundError,
    PaymentRefundTransientError,
)
from app.domain.payment.event.refund import (
    EVENT_TYPE_PAYMENT_REFUND_COMPLETED,
    EVENT_TYPE_PAYMENT_REFUND_FAILED,
    SCHEMA_VERSION,
    TOPIC_ORDER_REFUND_REQUESTED,
    TOPIC_PAYMENT_REFUND_COMPLETED,
    TOPIC_PAYMENT_REFUND_FAILED,
    OrderRefundRequestedPayload,
    PaymentRefundCompletedPayload,
    PaymentRefundFailedPayload,
)
from app.database.session import UnitOfWork, transactional
from app.core.outbox.repository import ProcessedEventRepository
from app.core.outbox.enqueue import enqueue_event
from app.core.logger import get_logger


logger = get_logger("event.refund_requested")


class OrderRefundRequestedEventHandler:

    def __init__(
        self,
        uow: UnitOfWork,
        store_payment_info_service: StorePaymentInfoService,
        payment_gateway_service: PaymentGatewayService,
    ):
        self.uow = uow
        self.store_payment_info_service = store_payment_info_service
        self.payment_gateway_service = payment_gateway_service


    async def handle(self, msg: ConsumerRecord) -> None:
        event_id = _extract_event_id(msg)
        try:
            payload = OrderRefundRequestedPayload.model_validate(msg.value)
        except ValidationError:
            logger.exception(
                "[CRITICAL] payload 검증 실패 skip event_id={} value={}",
                event_id, msg.value,
            )
            return

        await self._process(event_id=event_id, payload=payload)


    @transactional
    async def _process(
        self, *, event_id: UUID, payload: OrderRefundRequestedPayload,
    ) -> None:
        is_new = await ProcessedEventRepository(self._session).try_mark(
            event_id=event_id, topic=TOPIC_ORDER_REFUND_REQUESTED,
        )
        if not is_new:
            logger.info(
                "중복 이벤트 skip event_id={} payment_id={}",
                event_id, payload.payment_id,
            )
            return

        # 1) secret_key lookup
        try:
            info = await self.store_payment_info_service.get_complete_by_store(
                payload.store_id,
            )
        except (PaymentInfoMissingError, PaymentInfoIncompleteError) as e:
            logger.error(
                "[CRITICAL] 환불 불가 — store_payment_info 누락 "
                "payment_id={} store_id={}: {}",
                payload.payment_id, payload.store_id, e,
            )
            await self._enqueue_failed(
                payload=payload, error_kind="config_missing", error_detail=str(e),
            )
            return

        # 2) PortOne refund 호출 — 외부.
        try:
            await self.payment_gateway_service.refund(
                payment_id=payload.payment_id,
                secret_key=info.portone_secret_key,
                reason=payload.reason,
            )
        except PaymentRefundTransientError:
            # 5xx / 네트워크 — raise 로 tx rollback. try_mark 도 롤백 → 재배달 시 다시 시도.
            logger.warning(
                "PortOne 환불 transient — retry 예정 payment_id={}", payload.payment_id,
            )
            raise
        except PaymentRefundError as e:
            # PortOne 4xx — 이미 취소됐거나 결제 없음. terminal. failed 이벤트 발행.
            logger.error(
                "[CRITICAL] PortOne 환불 거부 (terminal) payment_id={}: {}",
                payload.payment_id, e,
            )
            await self._enqueue_failed(
                payload=payload, error_kind="portone_refused", error_detail=str(e),
            )
            return

        # 3) 성공 — completed 이벤트 발행. requested 의 모든 필드를 echo.
        # 손으로 필드를 하나하나 옮기면 schema 진화 시 누락 위험 (e.g., v2 의 store_name /
        # customer_id 누락 사고). 두 schema 가 의도적으로 동일 필드 set 이므로 model_dump
        # 로 통째 echo — 향후 v3 필드 추가에도 자동으로 안전.
        completed = PaymentRefundCompletedPayload(**payload.model_dump())
        await enqueue_event(
            self._session,
            aggregate_type="Payment",
            aggregate_id=payload.payment_id,
            event_type=EVENT_TYPE_PAYMENT_REFUND_COMPLETED,
            topic=TOPIC_PAYMENT_REFUND_COMPLETED,
            payload=completed.model_dump(),
            headers={"schema_version": SCHEMA_VERSION},
        )
        logger.info("환불 성공 → completed 발행 payment_id={}", payload.payment_id)


    async def _enqueue_failed(
        self,
        *,
        payload: OrderRefundRequestedPayload,
        error_kind: str,
        error_detail: str,
    ) -> None:
        failed = PaymentRefundFailedPayload(
            payment_id=payload.payment_id,
            store_id=payload.store_id,
            error_kind=error_kind,
            error_detail=error_detail,
        )
        await enqueue_event(
            self._session,
            aggregate_type="Payment",
            aggregate_id=payload.payment_id,
            event_type=EVENT_TYPE_PAYMENT_REFUND_FAILED,
            topic=TOPIC_PAYMENT_REFUND_FAILED,
            payload=failed.model_dump(),
            headers={"schema_version": SCHEMA_VERSION},
        )


def _extract_event_id(msg: ConsumerRecord) -> UUID:
    headers = {k: v.decode("utf-8") for k, v in (msg.headers or [])}
    raw = headers.get("event_id")
    if raw is None:
        raise ValueError(f"event_id 헤더 누락 offset={msg.offset}")
    return UUID(raw)
