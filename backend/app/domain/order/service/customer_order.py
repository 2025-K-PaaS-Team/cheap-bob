"""customer-side 주문 조회/취소/픽업완료."""
from typing import Optional
from fastapi import BackgroundTasks
from datetime import datetime, timedelta, timezone

from app.util.comma_separated import parse_comma_separated_string
from app.domain.seller.service.store_utils import get_main_image_url
from app.domain.seller.service.seller_store_read import SellerStoreReadService
from app.domain.seller.service.seller_store_image import SellerStoreImageService
from app.domain.seller.service.seller_product import SellerProductService
from app.domain.order.service.qr_callback_cache import QRCallbackCacheService
from app.domain.order.service.qr import validate_qr_data
from app.domain.order.service.exception import (
    OrderAlreadyCanceledError,
    OrderAlreadyCompletedError,
    OrderNotAcceptedError,
    OrderNotFoundError,
    OrderNotInReservationError,
    OrderOwnershipMismatchError,
    OrderQrInvalidError,
    OrderRefundError,
)
from app.domain.order.schema.order import (
    CustomerOrderItemResponse,
    CustomerOrderListResponse,
    CustomerTodayOrderItemResponse,
    CustomerTodayOrderListResponse,
    OrderCancelResponse,
    OrderItemResponse,
    TodayAlarmOrderCard,
    TodayAlarmResponse,
)
from app.domain.order.repository.order_history_item import OrderHistoryItemRepository
from app.domain.order.repository.order_current_item import OrderCurrentItemRepository
from app.domain.order.dto.order import OrderStatus
from app.database.session import UnitOfWork, transactional


_KST = timezone(timedelta(hours=9))


class CustomerOrderService:

    def __init__(
        self,
        uow: UnitOfWork,
        history_repo: OrderHistoryItemRepository,
        seller_store_read_service: SellerStoreReadService,
        seller_store_image_service: SellerStoreImageService,
        seller_product_service: SellerProductService,
        payment_gateway_service,
        store_payment_info_service,
    ):
        self.uow = uow
        self.history_repo = history_repo
        self.seller_store_read_service = seller_store_read_service
        self.seller_store_image_service = seller_store_image_service
        self.seller_product_service = seller_product_service
        self.payment_gateway_service = payment_gateway_service
        self.store_payment_info_service = store_payment_info_service


    # ───────── list ─────────


    async def list_orders(self, customer_email: str) -> CustomerOrderListResponse:
        current_orders = await self._list_current_for_customer(customer_email)
        history_orders = await self.history_repo.get_customer_history(customer_email)

        # 과거 주문 응답에 main_image_url 을 결합 — seller service 호출.
        history_store_ids = list({o.store_id for o in history_orders})
        store_main_images = await self.seller_store_image_service.get_main_image_urls(
            history_store_ids,
        )

        responses: list[CustomerOrderItemResponse] = []
        for o in current_orders:
            responses.append(_customer_order_response(o))
        for o in history_orders:
            responses.append(_customer_order_response_from_history(
                o, main_image_url=store_main_images.get(o.store_id),
            ))

        responses.sort(
            key=lambda x: max(
                filter(None, [x.reservation_at, x.accepted_at, x.completed_at, x.canceled_at]),
            ),
            reverse=True,
        )
        return CustomerOrderListResponse(orders=responses, total=len(responses))


    async def list_today_orders(
        self, customer_email: str,
    ) -> CustomerTodayOrderListResponse:
        orders = await self._list_today_for_customer(customer_email)
        responses: list[CustomerTodayOrderItemResponse] = []
        for o in orders:
            op = o.product.store.today_operation_info
            responses.append(CustomerTodayOrderItemResponse(
                **_customer_order_response(o).model_dump(),
                pickup_start_time=op.pickup_start_time.strftime("%H:%M"),
                pickup_end_time=op.pickup_end_time.strftime("%H:%M"),
            ))
        responses.sort(
            key=lambda x: max(
                filter(None, [x.reservation_at, x.accepted_at, x.completed_at, x.canceled_at]),
            ),
            reverse=True,
        )
        return CustomerTodayOrderListResponse(orders=responses, total=len(responses))


    async def get_today_alarm(self, customer_email: str) -> TodayAlarmResponse:
        orders = await self._list_today_alarm_for_customer(customer_email)

        cards: list[TodayAlarmOrderCard] = []
        for o in orders:
            op = o.product.store.today_operation_info
            base = {
                "payment_id": o.payment_id,
                "quantity": o.quantity,
                "price": o.price,
                "sale": o.sale,
                "total_amount": o.total_amount,
                "store_name": o.product.store.store_name,
                "product_name": o.product.product_name,
                "pickup_start_time": op.pickup_start_time.strftime("%H:%M"),
                "pickup_end_time": op.pickup_end_time.strftime("%H:%M"),
            }
            if o.reservation_at:
                cards.append(TodayAlarmOrderCard(
                    **base, order_time=o.reservation_at, status=OrderStatus.reservation,
                ))
            if o.accepted_at:
                cards.append(TodayAlarmOrderCard(
                    **base, order_time=o.accepted_at, status=OrderStatus.accept,
                ))
            if o.canceled_at:
                cards.append(TodayAlarmOrderCard(
                    **base, order_time=o.canceled_at, status=OrderStatus.cancel,
                ))

        cards.sort(key=lambda x: x.order_time, reverse=True)
        return TodayAlarmResponse(alarm_cards=cards, total=len(cards))


    # ───────── detail / complete pickup / cancel ─────────


    @transactional
    async def get_detail(self, payment_id: str) -> OrderItemResponse:
        order = await OrderCurrentItemRepository(
            self._session,
        ).get_order_with_store_relation(payment_id)
        if order is None:
            raise OrderNotFoundError("주문을 찾을 수 없습니다")
        return _order_response(order)


    @transactional
    async def complete_pickup(
        self, *, customer_email: str, payment_id: str, qr_data: str,
    ) -> OrderItemResponse:
        repo = OrderCurrentItemRepository(self._session)
        order = await repo.get_order_with_store_relation(payment_id)
        if order is None:
            raise OrderNotFoundError("주문을 찾을 수 없습니다")
        if order.status == OrderStatus.complete:
            raise OrderAlreadyCompletedError("이미 픽업이 완료된 주문입니다")
        if order.status != OrderStatus.accept:
            raise OrderNotAcceptedError("주문이 수락되지 않았습니다")

        is_valid, parsed, error_msg = validate_qr_data(qr_data, customer_email)
        if not is_valid:
            raise OrderQrInvalidError(error_msg)

        # 세 가지 ID 가 모두 일치해야 한다 — JWT / QR / DB 주문의 customer_id.
        if not (customer_email == parsed["customer_id"] == order.customer_id):
            raise OrderOwnershipMismatchError("권한이 없는 소비자입니다")
        if parsed["payment_id"] != payment_id:
            raise OrderQrInvalidError("잘못된 QR 코드입니다")
        if parsed["product_id"] != order.product_id:
            raise OrderOwnershipMismatchError("상품 정보가 일치하지 않습니다")

        completed = await repo.complete_order(payment_id)

        # 실패는 critical 하지 않다 — TTL 30초 후 자동 만료. 예외는 무시.
        try:
            await QRCallbackCacheService.set_completed(payment_id)
        except Exception:
            pass

        # completed 는 relationship 이 lazy 일 수 있어 원본 order 의 필드를 사용.
        return _order_response(order, override_status=completed.status,
                                override_completed_at=completed.completed_at)


    async def cancel(
        self,
        *,
        customer_email: str,
        payment_id: str,
        reason: str,
        background_tasks: BackgroundTasks,
    ) -> OrderCancelResponse:
        from app.domain.payment.service.exception import (
            PaymentInfoIncompleteError,
            PaymentInfoMissingError,
            PaymentRefundError,
        )
        from app.core.email.notifier import send_customer_cancel_email

        order = await self._get_with_product_relation(payment_id)
        if order is None:
            raise OrderNotFoundError("주문을 찾을 수 없습니다")
        if order.status == OrderStatus.cancel:
            raise OrderAlreadyCanceledError("이미 취소된 주문입니다")
        if order.status in (OrderStatus.accept, OrderStatus.complete):
            raise OrderNotInReservationError("이미 처리 중인 주문은 취소할 수 없습니다")

        try:
            payment_info = await self.store_payment_info_service.get_complete_by_store(
                order.product.store_id,
            )
        except (PaymentInfoMissingError, PaymentInfoIncompleteError) as e:
            raise OrderRefundError(str(e))

        try:
            await self.payment_gateway_service.refund(
                payment_id=payment_id,
                secret_key=payment_info.portone_secret_key,
                reason=reason,
            )
        except PaymentRefundError as e:
            raise OrderRefundError(str(e))

        quantity = await self._cancel_record(payment_id, reason)
        await self.seller_product_service.restore_purchased_stock(
            product_id=order.product_id, quantity=quantity,
        )

        store = await self.seller_store_read_service.get_with_full_info(
            order.product.store_id,
        )
        background_tasks.add_task(
            send_customer_cancel_email, customer_email, store.store_name,
        )

        return OrderCancelResponse(
            payment_id=payment_id,
            quantity=order.quantity,
            price=order.price,
            sale=order.sale,
            total_amount=order.total_amount,
        )


    # ───────── private — transactional helpers ─────────


    @transactional
    async def _list_current_for_customer(self, customer_email: str):
        return await OrderCurrentItemRepository(
            self._session,
        ).get_customer_current_orders(customer_email)


    @transactional
    async def _list_today_for_customer(self, customer_email: str):
        today = datetime.now(_KST).weekday()
        return await OrderCurrentItemRepository(
            self._session,
        ).get_customer_current_orders_with_pickup_time(customer_email, today)


    @transactional
    async def _list_today_alarm_for_customer(self, customer_email: str):
        today = datetime.now(_KST).weekday()
        return await OrderCurrentItemRepository(
            self._session,
        ).get_today_alarm_orders(customer_email, today)


    @transactional
    async def _get_with_product_relation(self, payment_id: str):
        return await OrderCurrentItemRepository(
            self._session,
        ).get_order_with_product_relation(payment_id)


    @transactional
    async def _cancel_record(self, payment_id: str, reason: str) -> int:
        return await OrderCurrentItemRepository(self._session).cancel_order(
            payment_id, cancel_reason=reason,
        )


def _customer_order_response(order) -> CustomerOrderItemResponse:
    return CustomerOrderItemResponse(
        payment_id=order.payment_id,
        customer_id=order.customer_id,
        customer_nickname=order.customer.detail.nickname,
        customer_phone_number=order.customer.detail.phone_number,
        product_id=order.product_id,
        product_name=order.product.product_name,
        store_id=order.product.store_id,
        store_name=order.product.store.store_name,
        main_image_url=get_main_image_url(order.product.store),
        quantity=order.quantity,
        price=order.price,
        sale=order.sale,
        total_amount=order.total_amount,
        status=order.status,
        reservation_at=order.reservation_at,
        accepted_at=order.accepted_at,
        completed_at=order.completed_at,
        canceled_at=order.canceled_at,
        cancel_reason=order.cancel_reason,
        preferred_menus=parse_comma_separated_string(order.preferred_menus),
        nutrition_types=parse_comma_separated_string(order.nutrition_types),
        allergies=parse_comma_separated_string(order.allergies),
        topping_types=parse_comma_separated_string(order.topping_types),
    )


def _customer_order_response_from_history(
    h, *, main_image_url: Optional[str],
) -> CustomerOrderItemResponse:
    return CustomerOrderItemResponse(
        payment_id=h.payment_id,
        customer_id=h.customer_id,
        customer_nickname=h.customer_nickname,
        customer_phone_number=h.customer_phone_number,
        product_id=h.product_id,
        product_name=h.product_name,
        store_id=h.store_id,
        store_name=h.store_name,
        main_image_url=main_image_url,
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


def _order_response(
    order,
    *,
    override_status: Optional[OrderStatus] = None,
    override_completed_at: Optional[datetime] = None,
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
        accepted_at=order.accepted_at,
        completed_at=override_completed_at or order.completed_at,
        canceled_at=order.canceled_at,
        cancel_reason=order.cancel_reason,
        preferred_menus=parse_comma_separated_string(order.preferred_menus),
        nutrition_types=parse_comma_separated_string(order.nutrition_types),
        allergies=parse_comma_separated_string(order.allergies),
        topping_types=parse_comma_separated_string(order.topping_types),
    )
