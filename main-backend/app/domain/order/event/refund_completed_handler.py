"""payment.refund.completed 이벤트 핸들러 — main-backend (consumer) 측.

payment-backend 가 PortOne 환불 성공 (혹은 이미 취소됨) 을 알리는 메시지를 받아:
  1. ProcessedEvent.try_mark — 중복이면 즉시 return.
  2. OrderCurrentItem.cancel_order — 주문 상태를 cancel 로 전이 + quantity 반환.
  3. SellerProductService.restore_purchased_stock — purchased_quantity 복원.
  4. cancel 이메일 발송 — tx 밖에서 best-effort (외부 IO).

DB 변경 (1~3) 은 `@transactional` 한 트랜잭션. 이메일 (4) 은 tx commit 이후.
이메일 실패는 logger.exception 만 — DB 상태는 이미 일관 (운영자 알람으로 처리).

멱등성:
  - ProcessedEvent PK = event_id — 같은 이벤트의 재배달은 즉시 skip (이메일 중복 발송 방지).
  - cancel_order 는 idempotent (이미 cancel 이면 quantity 0 반환).
  - restore_stock 는 quantity 0 일 때 호출 skip 으로 보호.
"""
from uuid import UUID
from pydantic import ValidationError
from aiokafka import ConsumerRecord

from app.domain.seller.service.seller_product import SellerProductService
from app.domain.order.repository.order_current_item import OrderCurrentItemRepository
from app.domain.order.event.refund import (
    TOPIC_PAYMENT_REFUND_COMPLETED,
    PaymentRefundCompletedPayload,
)
from app.database.session import UnitOfWork, transactional
from app.core.outbox.repository import ProcessedEventRepository
from app.core.logger import get_logger
from app.core.email.notifier import send_seller_cancel_email


logger = get_logger("event.refund_completed")


class PaymentRefundCompletedEventHandler:

    def __init__(
        self,
        uow: UnitOfWork,
        seller_product_service: SellerProductService,
    ):
        self.uow = uow
        self.seller_product_service = seller_product_service


    async def handle(self, msg: ConsumerRecord) -> None:
        event_id = _extract_event_id(msg)
        try:
            payload = PaymentRefundCompletedPayload.model_validate(msg.value)
        except ValidationError:
            logger.exception(
                "[CRITICAL] payload 검증 실패 skip event_id={} value={}",
                event_id, msg.value,
            )
            return

        applied = await self._apply(event_id=event_id, payload=payload)
        if not applied:
            return

        # 이메일은 tx 밖 best-effort. DB cancel 은 이미 commit 됐다 — 실패해도 상태 일관.
        try:
            await send_seller_cancel_email(payload.customer_id, payload.store_name)
        except Exception:
            logger.exception(
                "취소 이메일 발송 실패 customer={} payment_id={}",
                payload.customer_id, payload.payment_id,
            )


    @transactional
    async def _apply(
        self, *, event_id: UUID, payload: PaymentRefundCompletedPayload,
    ) -> bool:
        """Returns True 면 신규 적용 (이메일 발송 필요), False 면 중복 (skip)."""
        is_new = await ProcessedEventRepository(self._session).try_mark(
            event_id=event_id, topic=TOPIC_PAYMENT_REFUND_COMPLETED,
        )
        if not is_new:
            logger.info(
                "중복 이벤트 skip event_id={} payment_id={}",
                event_id, payload.payment_id,
            )
            return False

        # cancel_order — 이미 cancel 이면 quantity 0 반환 (idempotent).
        quantity = await OrderCurrentItemRepository(self._session).cancel_order(
            payload.payment_id, payload.reason,
        )
        # restore_stock — quantity 양수일 때만 (idempotency 2차 방어).
        if quantity:
            await self.seller_product_service.restore_purchased_stock(
                product_id=payload.product_id, quantity=quantity,
            )

        logger.info(
            "환불 완료 처리 payment_id={} product_id={} quantity={}",
            payload.payment_id, payload.product_id, quantity,
        )
        return True


def _extract_event_id(msg: ConsumerRecord) -> UUID:
    headers = {k: v.decode("utf-8") for k, v in (msg.headers or [])}
    raw = headers.get("event_id")
    if raw is None:
        raise ValueError(f"event_id 헤더 누락 offset={msg.offset}")
    return UUID(raw)
