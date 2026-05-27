"""/seller/store/close — 가게 마감 + 진행중 주문 환불 시작.

Saga 분해:
  - 본 메서드: 사전 체크 (결제 설정 존재 여부) + today closed + 활성 주문별 outbox 이벤트 발행.
    한 트랜잭션에서 운영 상태 변경과 N개 이벤트 enqueue 가 commit — dual-write 없음.
    응답 시간이 주문 개수에 비례하지 않는다.
  - 실제 환불 / OrderCurrentItem cancel / stock restore 는:
      payment-backend (PortOne refund) → payment.refund.completed →
        main-backend.PaymentRefundCompletedHandler (cancel + restore_stock).
    실패는 payment.refund.failed → CRITICAL 로깅, 주문 상태 그대로 (운영자 보정).

사전 체크 (has_complete_info) 는 sync 유지 — 결제 설정 누락 시 즉시 사용자에게 명시적 에러.
"""
from typing import Tuple

from app.domain.seller.service.exception import StorePaymentMissingError
from app.domain.seller.repository.store_operation_info import (
    StoreOperationInfoRepository,
)
from app.domain.order.service.order_query import OrderQueryService
from app.domain.order.event.refund import (
    EVENT_TYPE_ORDER_REFUND_REQUESTED,
    SCHEMA_VERSION,
    TOPIC_ORDER_REFUND_REQUESTED,
    OrderRefundRequestedPayload,
)
from app.domain.order.dto.order import OrderStatus
from app.database.session import UnitOfWork, transactional
from app.core.outbox.enqueue import enqueue_event
from app.core.logger import get_logger
from app.core.internal_client.payment import (
    InternalPaymentClient,
    PaymentServiceUnavailableError,
)


logger = get_logger("seller.service.seller_store_close")


class SellerStoreCloseService:
    """가게 마감 + 진행중 주문 환불 트리거.

    환불 진행은 비동기 (이벤트). 응답 count 는 "환불 진행 시작된 개수" — "완료된 개수" 아님.
    호출자/UI 는 그렇게 안내해야 한다.
    """

    def __init__(
        self,
        uow: UnitOfWork,
        order_query_service: OrderQueryService,
        internal_payment_client: InternalPaymentClient,
    ):
        self.uow = uow
        self.order_query_service = order_query_service
        self.internal_payment_client = internal_payment_client


    async def close(self, store_id: str) -> Tuple[int, str]:
        """가게 마감 + 진행중 주문 환불 시작.

        Returns: (refund_started_count, 안내 메시지).
        """
        # 사전 — 결제 설정 누락 시 즉시 명시적 에러 (UX). sync HTTP + CB + retry.
        try:
            has = await self.internal_payment_client.has_complete_info(store_id)
        except PaymentServiceUnavailableError as e:
            raise StorePaymentMissingError(f"payment-backend 일시 장애: {e.detail}")
        if not has:
            raise StorePaymentMissingError("가게의 결제 설정이 완료되지 않았습니다")

        refund_count = await self._close_and_emit_refunds(store_id)
        message = (
            f"가게가 마감되었습니다. {refund_count}건 환불을 진행합니다"
            if refund_count
            else "가게가 마감되었습니다"
        )
        return refund_count, message


    @transactional
    async def _close_and_emit_refunds(self, store_id: str) -> int:
        """한 트랜잭션에서:
          1. 오늘 운영 정보 is_currently_open=False
          2. 활성 주문 (reservation/accept) 목록 조회
          3. 주문 1건당 order.refund.requested outbox enqueue

        commit 후 OutboxRelay 가 비동기로 Kafka 에 발행. 본 메서드는 즉시 리턴.
        """
        operation_repo = StoreOperationInfoRepository(self._session)
        today_op = await operation_repo.get_today_operation_info(store_id)
        if today_op:
            await operation_repo.update_open_status(
                operation_id=today_op.operation_id, is_currently_open=False,
            )

        # order_query_service.list_store_current_orders 는 @transactional — 같은 세션 공유.
        # relations 로딩 (order.product.store.store_name) 까지 같이 가져온다.
        current_orders = await self.order_query_service.list_store_current_orders(
            store_id,
        )

        active = {OrderStatus.reservation, OrderStatus.accept}
        reason = "'기타 사정' 으로 주문이 취소되었어요."

        refund_count = 0
        for order in current_orders:
            if order.status not in active:
                continue
            payload = OrderRefundRequestedPayload(
                payment_id=order.payment_id,
                store_id=store_id,
                store_name=order.product.store.store_name,
                customer_id=order.customer_id,
                product_id=order.product_id,
                quantity=order.quantity,
                reason=reason,
            )
            await enqueue_event(
                self._session,
                aggregate_type="Payment",
                aggregate_id=order.payment_id,
                event_type=EVENT_TYPE_ORDER_REFUND_REQUESTED,
                topic=TOPIC_ORDER_REFUND_REQUESTED,
                payload=payload.model_dump(),
                headers={"schema_version": SCHEMA_VERSION},
            )
            refund_count += 1

        logger.info(
            "가게 {} 마감 — 환불 이벤트 {} 건 enqueue", store_id, refund_count,
        )
        return refund_count
