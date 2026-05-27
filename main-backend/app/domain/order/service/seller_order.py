"""seller-side 주문 조회/수락/취소/QR/대시보드.

payment 도메인 분리 후 refund 는 payment-backend internal API 한 번에 위임.
"""
from typing import Optional
from fastapi import BackgroundTasks
from datetime import datetime, timezone
from collections import defaultdict

from app.util.comma_separated import parse_comma_separated_string
from app.domain.seller.service.seller_store_read import SellerStoreReadService
from app.domain.seller.service.seller_product import SellerProductService
from app.domain.order.service.qr import encode_qr_data
from app.domain.order.service.order_query import OrderQueryService
from app.domain.order.service.exception import (
    OrderAlreadyCanceledError,
    OrderNotFoundError,
    OrderNotInReservationError,
    OrderOwnershipMismatchError,
    OrderRefundError,
)
from app.domain.order.schema.order import (
    OrderCancelResponse,
    OrderItemResponse,
    OrderListResponse,
    SellerPickupQRResponse,
)
from app.domain.order.schema.dashboard import DashboardResponse, DashboardStockItem
from app.domain.order.repository.order_history_item import OrderHistoryItemRepository
from app.domain.order.repository.order_current_item import OrderCurrentItemRepository
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
    PaymentServiceError,
    PaymentServiceUnavailableError,
)
from app.core.email.notifier import (
    send_order_accepted_email,
    send_seller_cancel_email,
)


logger = get_logger("order.service.seller_order")


class SellerOrderService:

    def __init__(
        self,
        uow: UnitOfWork,
        history_repo: OrderHistoryItemRepository,
        seller_store_read_service: SellerStoreReadService,
        seller_product_service: SellerProductService,
        order_query_service: OrderQueryService,
        internal_payment_client: InternalPaymentClient,
    ):
        self.uow = uow
        self.history_repo = history_repo
        self.seller_store_read_service = seller_store_read_service
        self.seller_product_service = seller_product_service
        self.order_query_service = order_query_service
        self.internal_payment_client = internal_payment_client


    # ───────── list ─────────


    @transactional
    async def list_orders(self, store_id: str) -> OrderListResponse:
        current_orders = await OrderCurrentItemRepository(
            self._session,
        ).get_store_orders_with_relations(store_id)
        history_orders = await self.history_repo.get_store_history(store_id)

        responses = [_seller_response(o) for o in current_orders]
        responses.extend(_seller_response_from_history(h, store_id) for h in history_orders)

        responses.sort(
            key=lambda x: max(
                filter(None, [x.reservation_at, x.accepted_at, x.completed_at, x.canceled_at]),
            ),
            reverse=True,
        )
        return OrderListResponse(orders=responses, total=len(responses))


    @transactional
    async def list_today_orders(self, store_id: str) -> OrderListResponse:
        orders = await OrderCurrentItemRepository(
            self._session,
        ).get_store_current_orders_with_relations(store_id)
        responses = [_seller_response(o) for o in orders]
        responses.sort(
            key=lambda x: max(
                filter(None, [x.reservation_at, x.accepted_at, x.completed_at, x.canceled_at]),
            ),
            reverse=True,
        )
        return OrderListResponse(orders=responses, total=len(responses))


    # ───────── transitions ─────────


    async def accept_order(
        self, *, store_id: str, payment_id: str, background_tasks: BackgroundTasks,
    ) -> OrderItemResponse:
        order, updated = await self._accept_record(
            store_id=store_id, payment_id=payment_id,
        )
        if order is None:
            raise OrderNotFoundError("주문을 찾을 수 없습니다")
        if updated is None:
            raise OrderNotInReservationError("이미 처리된 주문입니다")

        store = await self.seller_store_read_service.get_with_full_info(store_id)
        background_tasks.add_task(
            send_order_accepted_email, order.customer_id, store.store_name,
        )
        return _seller_response(order, override_status=updated.status,
                                override_accepted_at=updated.accepted_at)


    async def cancel_order(
        self,
        *,
        store_id: str,
        payment_id: str,
        reason: str,
        background_tasks: BackgroundTasks,
    ) -> OrderCancelResponse:
        order = await self._get_with_product_relation(payment_id)
        if order is None:
            raise OrderNotFoundError("주문을 찾을 수 없습니다")
        if order.product.store_id != store_id:
            raise OrderOwnershipMismatchError("본인 가게 주문만 취소할 수 있습니다")
        if order.status == OrderStatus.cancel:
            raise OrderAlreadyCanceledError("이미 취소된 주문입니다")

        try:
            await self.internal_payment_client.refund(
                payment_id=payment_id, store_id=store_id, reason=reason,
            )
        except (PaymentServiceError, PaymentServiceUnavailableError) as e:
            raise OrderRefundError(str(e))

        try:
            quantity = await self._cancel_record(payment_id, reason)
        except Exception:
            logger.exception(
                "[CRITICAL] 환불 성공 후 주문 취소 갱신 실패 - payment_id={}, store={}",
                payment_id, store_id,
            )
            quantity = order.quantity
        try:
            await self.seller_product_service.restore_purchased_stock(
                product_id=order.product_id, quantity=quantity,
            )
        except Exception:
            logger.exception(
                "[CRITICAL] 환불 성공 후 재고 복원 실패 - payment_id={}, product={}, quantity={}",
                payment_id, order.product_id, quantity,
            )

        store = await self.seller_store_read_service.get_with_full_info(store_id)
        background_tasks.add_task(
            send_seller_cancel_email, order.customer_id, store.store_name,
        )

        return OrderCancelResponse(
            payment_id=payment_id,
            quantity=order.quantity,
            price=order.price,
            sale=order.sale,
            total_amount=order.total_amount,
        )


    # ───────── QR + Dashboard ─────────


    @transactional
    async def get_pickup_qr(
        self, *, store_id: str, payment_id: str,
    ) -> SellerPickupQRResponse:
        order = await OrderCurrentItemRepository(
            self._session,
        ).get_order_with_relations(payment_id)
        if order is None:
            raise OrderNotFoundError("주문을 찾을 수 없습니다")
        if order.product.store_id != store_id:
            raise OrderOwnershipMismatchError("본인 가게 주문만 QR 발급 가능합니다")
        if order.status != OrderStatus.accept:
            raise OrderNotInReservationError("주문이 수락되지 않았습니다")

        qr_data, created_at = encode_qr_data(
            customer_id=order.customer_id,
            payment_id=payment_id,
            product_id=order.product_id,
        )
        return SellerPickupQRResponse(
            payment_id=payment_id, qr_data=qr_data, created_at=created_at,
        )


    async def get_dashboard(self, store_id: str) -> DashboardResponse:
        purchased_qty_by_product = await self.order_query_service.store_purchased_quantities(
            store_id,
        )
        products = await self.seller_product_service.list_by_store(store_id)

        items = [
            DashboardStockItem(
                product_id=p.product_id,
                product_name=p.product_name,
                current_stock=p.initial_stock
                - purchased_qty_by_product.get(p.product_id, 0)
                + p.admin_adjustment,
                initial_stock=p.initial_stock,
                purchased_stock=purchased_qty_by_product.get(p.product_id, 0),
                adjustment_stock=p.admin_adjustment,
            )
            for p in products
        ]
        return DashboardResponse(items=items, total_items=len(items))


    # ───────── 스케줄러 worker 용 ─────────


    async def cancel_store_reservation_orders(
        self, *, store_id: str, store_name: str, reason: str,
    ) -> tuple[int, int, int]:
        """가게의 모든 reservation 상태 주문 환불 시작.

        sync 환불 루프 → outbox 이벤트로 전환. PortOne refund / OrderCurrentItem
        cancel / stock restore / 이메일 발송은 saga 의 뒷 단계 
        (payment-backend → PaymentRefundCompletedEventHandler) 가 책임.

        Returns: (started, failed, total_amount).
          - started: 환불 이벤트 발행한 주문 수 (실제 환불 완료가 아님).
          - failed: 결제 설정 누락/일시 장애로 이벤트조차 못 보낸 주문 수.
          - total_amount: started 합산 금액.
        """
        # 사전 — 결제 설정 누락이면 모든 주문에 대해 동일 실패가 나니, 한 번에 짧게 차단.
        try:
            has = await self.internal_payment_client.has_complete_info(store_id)
        except PaymentServiceUnavailableError:
            logger.exception(
                "[{}] payment-backend 일시 장애 — reservation 주문 환불 보류", store_name,
            )
            return 0, 0, 0
        if not has:
            logger.error("[{}] 결제 설정이 없어 reservation 주문 환불 불가", store_name)
            return 0, 0, 0

        started, total_amount = await self._emit_refund_events_for_store(
            store_id=store_id, store_name=store_name, reason=reason,
        )
        return started, 0, total_amount


    async def refund_all_uncompleted(self) -> tuple[int, int, int]:
        """모든 가게의 reservation/accept 상태 미완료 주문 환불 시작.

        saga 패턴. 사전 체크 (가게별 has_complete_info) 후 살아남은 가게의
        모든 주문에 대해 1 트랜잭션 안에서 outbox 이벤트 일괄 발행.

        Returns: (started, failed, total_amount).
        """
        # 1. 미완료 주문 목록 (relations 포함).
        all_orders = await self._list_all_current_with_relations()
        uncompleted = [
            o for o in all_orders
            if o.status in (OrderStatus.reservation, OrderStatus.accept)
        ]
        if not uncompleted:
            logger.info("환불 처리할 미완료 주문이 없습니다")
            return 0, 0, 0

        orders_by_store: dict[str, list] = defaultdict(list)
        for o in uncompleted:
            orders_by_store[o.product.store_id].append(o)

        # 2. 가게별 사전 has_complete_info — tx 밖에서 sync HTTP (CB 보호).
        eligible: dict[str, list] = {}
        failed = 0
        for store_id, store_orders in orders_by_store.items():
            try:
                has = await self.internal_payment_client.has_complete_info(store_id)
            except PaymentServiceUnavailableError:
                logger.exception(
                    "가게 {} payment-backend 일시 장애 — {}개 주문 환불 보류",
                    store_id, len(store_orders),
                )
                failed += len(store_orders)
                continue
            if not has:
                logger.error(
                    "가게 {}의 결제 설정이 없어 {}개 주문 환불 실패",
                    store_id, len(store_orders),
                )
                failed += len(store_orders)
                continue
            eligible[store_id] = store_orders

        if not eligible:
            return 0, failed, 0

        # 3. 살아남은 가게의 모든 이벤트를 한 tx 로 발행.
        started, total_amount = await self._emit_refund_events_for_stores(
            eligible, reason="영업 시간 종료로 인한 자동 환불",
        )
        return started, failed, total_amount


    @transactional
    async def _emit_refund_events_for_store(
        self, *, store_id: str, store_name: str, reason: str,
    ) -> tuple[int, int]:
        """단일 가게 reservation 주문 → outbox 이벤트. (started, total_amount)."""
        orders = await OrderCurrentItemRepository(
            self._session,
        ).get_store_current_orders_with_relations(store_id)
        reservation_orders = [
            o for o in orders if o.status == OrderStatus.reservation
        ]
        if not reservation_orders:
            logger.info("[{}] 취소/환불 대상 reservation 주문 없음", store_name)
            return 0, 0

        started = 0
        total_amount = 0
        for order in reservation_orders:
            await self._enqueue_refund_requested(
                payment_id=order.payment_id,
                store_id=store_id,
                store_name=store_name,
                customer_id=order.customer_id,
                product_id=order.product_id,
                quantity=order.quantity,
                reason=reason,
            )
            started += 1
            total_amount += order.total_amount
            logger.info(
                "[{}] 주문 환불 이벤트 발행 - payment_id: {}, 고객: {}, 금액: {:,}원",
                store_name, order.payment_id, order.customer_id, order.total_amount,
            )
        return started, total_amount


    @transactional
    async def _emit_refund_events_for_stores(
        self, eligible: dict[str, list], reason: str,
    ) -> tuple[int, int]:
        """eligible 가게의 모든 미완료 주문에 대해 한 tx 로 이벤트 발행.

        (started, total_amount).
        """
        started = 0
        total_amount = 0
        for store_id, store_orders in eligible.items():
            store_name = store_orders[0].product.store.store_name
            for order in store_orders:
                await self._enqueue_refund_requested(
                    payment_id=order.payment_id,
                    store_id=store_id,
                    store_name=store_name,
                    customer_id=order.customer_id,
                    product_id=order.product_id,
                    quantity=order.quantity,
                    reason=reason,
                )
                started += 1
                total_amount += order.total_amount
                logger.info(
                    "주문 {} 환불 이벤트 발행 - 고객: {}, 상품: {}, 금액: {:,}원",
                    order.payment_id, order.customer_id,
                    order.product.product_name, order.total_amount,
                )
        return started, total_amount


    async def _enqueue_refund_requested(
        self,
        *,
        payment_id: str,
        store_id: str,
        store_name: str,
        customer_id: str,
        product_id: str,
        quantity: int,
        reason: str,
    ) -> None:
        """공통 enqueue helper — payload 구성 일관성."""
        payload = OrderRefundRequestedPayload(
            payment_id=payment_id,
            store_id=store_id,
            store_name=store_name,
            customer_id=customer_id,
            product_id=product_id,
            quantity=quantity,
            reason=reason,
        )
        await enqueue_event(
            self._session,
            aggregate_type="Payment",
            aggregate_id=payment_id,
            event_type=EVENT_TYPE_ORDER_REFUND_REQUESTED,
            topic=TOPIC_ORDER_REFUND_REQUESTED,
            payload=payload.model_dump(),
            headers={"schema_version": SCHEMA_VERSION},
        )


    async def complete_store_accepted_orders(
        self, *, store_id: str, store_name: str,
    ) -> tuple[int, int]:
        orders = await self.order_query_service.list_store_current_orders(store_id)
        accepted = [o for o in orders if o.status == OrderStatus.accept]
        if not accepted:
            logger.info("[{}] 완료 처리할 accept 주문 없음", store_name)
            return 0, 0

        completed = 0
        failed = 0
        for order in accepted:
            try:
                await self._complete_record(order.payment_id)
                completed += 1
                logger.info(
                    "[{}] 주문 자동 완료 - payment_id: {}, 고객: {}",
                    store_name, order.payment_id, order.customer_id,
                )
            except Exception:
                failed += 1
                logger.exception(
                    "[{}] 주문 {} 완료 처리 실패",
                    store_name, order.payment_id,
                )
        return completed, failed


    # ───────── private ─────────


    @transactional
    async def _list_all_current_with_relations(self):
        return await OrderCurrentItemRepository(
            self._session,
        ).get_all_orders_with_relations()


    @transactional
    async def _complete_record(self, payment_id: str):
        return await OrderCurrentItemRepository(self._session).complete_order(
            payment_id,
        )


    @transactional
    async def _accept_record(self, *, store_id: str, payment_id: str):
        repo = OrderCurrentItemRepository(self._session)
        order = await repo.get_order_with_relations(payment_id)
        if order is None:
            return None, None
        if order.product.store_id != store_id:
            raise OrderOwnershipMismatchError("본인 가게 주문만 처리할 수 있습니다")
        if order.status != OrderStatus.reservation:
            return order, None
        updated = await repo.update(
            payment_id,
            status=OrderStatus.accept,
            accepted_at=datetime.now(timezone.utc),
        )
        return order, updated


    @transactional
    async def _get_with_product_relation(self, payment_id: str):
        return await OrderCurrentItemRepository(
            self._session,
        ).get_order_with_relations(payment_id)


    @transactional
    async def _cancel_record(self, payment_id: str, reason: str) -> int:
        return await OrderCurrentItemRepository(self._session).cancel_order(
            payment_id, cancel_reason=reason,
        )


    @transactional
    async def assert_order_belongs_to_store(
        self, *, store_id: str, payment_id: str,
    ) -> None:
        order = await OrderCurrentItemRepository(
            self._session,
        ).get_order_with_relations(payment_id)
        if order is None:
            raise OrderNotFoundError("주문을 찾을 수 없습니다")
        if order.product.store_id != store_id:
            raise OrderOwnershipMismatchError("본인 가게 주문이 아닙니다")


def _seller_response(
    order,
    *,
    override_status: Optional[OrderStatus] = None,
    override_accepted_at: Optional[datetime] = None,
) -> OrderItemResponse:
    return OrderItemResponse(
        payment_id=order.payment_id,
        customer_id=order.customer_id,
        customer_nickname=order.customer.detail.nickname,
        customer_phone_number=order.customer.detail.phone_number,
        product_id=order.product_id,
        product_name=order.product.product_name,
        store_id=order.product.store_id,
        store_name=order.product.store.store_name,
        quantity=order.quantity,
        price=order.price,
        sale=order.sale,
        total_amount=order.total_amount,
        status=override_status or order.status,
        reservation_at=order.reservation_at,
        accepted_at=override_accepted_at or order.accepted_at,
        completed_at=order.completed_at,
        canceled_at=order.canceled_at,
        cancel_reason=order.cancel_reason,
        preferred_menus=parse_comma_separated_string(order.preferred_menus),
        nutrition_types=parse_comma_separated_string(order.nutrition_types),
        allergies=parse_comma_separated_string(order.allergies),
        topping_types=parse_comma_separated_string(order.topping_types),
    )


def _seller_response_from_history(h, store_id: str) -> OrderItemResponse:
    return OrderItemResponse(
        payment_id=h.payment_id,
        customer_id=h.customer_id,
        customer_nickname=h.customer_nickname,
        customer_phone_number=h.customer_phone_number,
        product_id=h.product_id,
        product_name=h.product_name,
        store_id=store_id,
        store_name=h.store_name,
        quantity=h.quantity,
        price=h.price,
        sale=h.sale,
        total_amount=h.total_amount,
        status=h.status,
        reservation_at=h.reservation_at,
        accepted_at=h.accepted_at,
        completed_at=h.completed_at,
        canceled_at=h.canceled_at,
        cancel_reason=h.cancel_reason,
        preferred_menus=parse_comma_separated_string(h.preferred_menus),
        nutrition_types=parse_comma_separated_string(h.nutrition_types),
        allergies=parse_comma_separated_string(h.allergies),
        topping_types=parse_comma_separated_string(h.topping_types),
    )
