"""Tests for ``app.domain.order.service.seller_order.SellerOrderService``."""
from types import SimpleNamespace
from test.unit.domain.order.seller_order_service.mock_factory import (
    BackgroundTasksFakeFactory,
)
from test.unit.domain.order.customer_order_service.model_factory import (
    OrderFactory,
    OrderHistoryFactory,
)
import pytest
from datetime import datetime, timezone

from app.domain.order.service.exception import (
    OrderAlreadyCanceledError,
    OrderNotFoundError,
    OrderNotInReservationError,
    OrderRefundError,
)
from app.domain.order.dto.order import OrderStatus
from app.core.internal_client.payment import (
    PaymentServiceError,
    PaymentServiceUnavailableError,
)


# ────────────────────────────────────────────────────────────────────
# list_orders
# ────────────────────────────────────────────────────────────────────

@pytest.mark.unit
class TestListOrders:

    async def test_returns_empty(self, service, order_repo_mock, history_repo_mock):
        order_repo_mock.get_store_orders_with_relations.return_value = []
        history_repo_mock.get_store_history.return_value = []

        result = await service.list_orders("STR_x")

        assert result.total == 0
        assert result.orders == []


    async def test_merges_current_and_history(
        self, service, order_repo_mock, history_repo_mock,
    ):
        current = [OrderFactory.create(store_id="STR_x")]
        history = [OrderHistoryFactory.create(store_id="STR_x")]
        order_repo_mock.get_store_orders_with_relations.return_value = current
        history_repo_mock.get_store_history.return_value = history

        result = await service.list_orders("STR_x")

        assert result.total == 2


# ────────────────────────────────────────────────────────────────────
# accept_order
# ────────────────────────────────────────────────────────────────────

@pytest.mark.unit
class TestAcceptOrder:

    async def test_raises_when_order_not_found(self, service, order_repo_mock):
        order_repo_mock.get_order_with_relations.return_value = None
        bt, _ = BackgroundTasksFakeFactory.create()
        with pytest.raises(OrderNotFoundError):
            await service.accept_order(
                store_id="STR_x", payment_id="PAY_missing", background_tasks=bt,
            )


    async def test_raises_when_not_in_reservation(self, service, order_repo_mock):
        order = OrderFactory.create(status=OrderStatus.accept, store_id="STR_x")
        order_repo_mock.get_order_with_relations.return_value = order
        bt, _ = BackgroundTasksFakeFactory.create()
        with pytest.raises(OrderNotInReservationError):
            await service.accept_order(
                store_id="STR_x", payment_id=order.payment_id, background_tasks=bt,
            )


    async def test_accepts_and_schedules_email(
        self, service, order_repo_mock, store_read_mock,
    ):
        order = OrderFactory.create(status=OrderStatus.reservation, store_id="STR_x")
        order_repo_mock.get_order_with_relations.return_value = order
        order_repo_mock.update.return_value = SimpleNamespace(
            status=OrderStatus.accept, accepted_at=datetime.now(timezone.utc),
        )
        store_read_mock.get_with_full_info.return_value = SimpleNamespace(store_name="가게")

        bt, tasks = BackgroundTasksFakeFactory.create()
        result = await service.accept_order(
            store_id="STR_x", payment_id=order.payment_id, background_tasks=bt,
        )

        assert result.status == OrderStatus.accept
        order_repo_mock.update.assert_awaited()
        # 수락 이메일 background task 등록.
        assert len(tasks) == 1


# ────────────────────────────────────────────────────────────────────
# cancel_order
# ────────────────────────────────────────────────────────────────────

@pytest.mark.unit
class TestCancelOrder:

    async def test_raises_when_order_not_found(self, service, order_repo_mock):
        order_repo_mock.get_order_with_relations.return_value = None
        bt, _ = BackgroundTasksFakeFactory.create()
        with pytest.raises(OrderNotFoundError):
            await service.cancel_order(
                store_id="STR_x",
                payment_id="PAY_missing",
                reason="가게 사정",
                background_tasks=bt,
            )


    async def test_raises_when_already_canceled(self, service, order_repo_mock):
        order = OrderFactory.create(status=OrderStatus.cancel, store_id="STR_x")
        order_repo_mock.get_order_with_relations.return_value = order
        bt, _ = BackgroundTasksFakeFactory.create()
        with pytest.raises(OrderAlreadyCanceledError):
            await service.cancel_order(
                store_id="STR_x",
                payment_id=order.payment_id,
                reason="가게 사정",
                background_tasks=bt,
            )


    async def test_raises_refund_error_on_payment_svc_fail(
        self, service, order_repo_mock, payment_client_mock,
    ):
        order = OrderFactory.create(status=OrderStatus.reservation, store_id="STR_x")
        order_repo_mock.get_order_with_relations.return_value = order
        payment_client_mock.refund.side_effect = PaymentServiceUnavailableError(
            503, "network",
        )
        bt, _ = BackgroundTasksFakeFactory.create()
        with pytest.raises(OrderRefundError):
            await service.cancel_order(
                store_id="STR_x",
                payment_id=order.payment_id,
                reason="가게 사정",
                background_tasks=bt,
            )


    async def test_refunds_and_restores_stock(
        self,
        service,
        order_repo_mock,
        payment_client_mock,
        product_service_mock,
    ):
        order = OrderFactory.create(
            status=OrderStatus.reservation, quantity=2, total_amount=20000,
            store_id="STR_x",
        )
        order_repo_mock.get_order_with_relations.return_value = order
        order_repo_mock.cancel_order.return_value = 2

        bt, tasks = BackgroundTasksFakeFactory.create()
        result = await service.cancel_order(
            store_id="STR_x",
            payment_id=order.payment_id,
            reason="가게 사정",
            background_tasks=bt,
        )

        payment_client_mock.refund.assert_awaited_once()
        product_service_mock.restore_purchased_stock.assert_awaited_once_with(
            product_id=order.product_id, quantity=2,
        )
        assert result.total_amount == 20000
        assert len(tasks) == 1


# ────────────────────────────────────────────────────────────────────
# get_pickup_qr
# ────────────────────────────────────────────────────────────────────

@pytest.mark.unit
class TestGetPickupQR:

    async def test_raises_when_not_found(self, service, order_repo_mock):
        order_repo_mock.get_order_with_relations.return_value = None
        with pytest.raises(OrderNotFoundError):
            await service.get_pickup_qr(store_id="STR_x", payment_id="PAY_missing")


    async def test_raises_when_not_accepted(self, service, order_repo_mock):
        order = OrderFactory.create(status=OrderStatus.reservation, store_id="STR_x")
        order_repo_mock.get_order_with_relations.return_value = order
        with pytest.raises(OrderNotInReservationError):
            await service.get_pickup_qr(store_id="STR_x", payment_id=order.payment_id)


    async def test_returns_qr_data_when_accepted(self, service, order_repo_mock):
        order = OrderFactory.create(
            status=OrderStatus.accept, payment_id="PAY_qr", store_id="STR_x",
        )
        order_repo_mock.get_order_with_relations.return_value = order

        result = await service.get_pickup_qr(store_id="STR_x", payment_id="PAY_qr")

        assert result.payment_id == "PAY_qr"
        assert isinstance(result.qr_data, str) and len(result.qr_data) > 0


# ────────────────────────────────────────────────────────────────────
# get_dashboard
# ────────────────────────────────────────────────────────────────────

@pytest.mark.unit
class TestGetDashboard:

    async def test_empty_when_no_products(
        self, service, order_query_mock, product_service_mock,
    ):
        order_query_mock.store_purchased_quantities.return_value = {}
        product_service_mock.list_by_store.return_value = []

        result = await service.get_dashboard("STR_x")

        assert result.total_items == 0
        assert result.items == []


    async def test_computes_current_stock_correctly(
        self, service, order_query_mock, product_service_mock,
    ):
        # current_stock = initial - purchased + admin_adjustment
        product = SimpleNamespace(
            product_id="PRD_x",
            product_name="치킨",
            initial_stock=10,
            admin_adjustment=2,
        )
        order_query_mock.store_purchased_quantities.return_value = {"PRD_x": 3}
        product_service_mock.list_by_store.return_value = [product]

        result = await service.get_dashboard("STR_x")

        assert result.total_items == 1
        item = result.items[0]
        assert item.product_id == "PRD_x"
        assert item.initial_stock == 10
        assert item.purchased_stock == 3
        assert item.adjustment_stock == 2
        assert item.current_stock == 9  # 10 - 3 + 2


    async def test_uses_zero_purchased_when_product_not_in_map(
        self, service, order_query_mock, product_service_mock,
    ):
        product = SimpleNamespace(
            product_id="PRD_y", product_name="피자",
            initial_stock=5, admin_adjustment=0,
        )
        order_query_mock.store_purchased_quantities.return_value = {}
        product_service_mock.list_by_store.return_value = [product]

        result = await service.get_dashboard("STR_x")

        assert result.items[0].purchased_stock == 0
        assert result.items[0].current_stock == 5


# ────────────────────────────────────────────────────────────────────
# cancel_store_reservation_orders — worker 엔트리포인트 (Phase 5.3: 이벤트 발행만 책임)
# ────────────────────────────────────────────────────────────────────

@pytest.mark.unit
class TestCancelStoreReservationOrders:

    async def test_returns_zero_when_payment_info_missing(
        self, service, payment_client_mock, enqueue_event_mock,
    ):
        payment_client_mock.has_complete_info.return_value = False
        started, failed, total = await service.cancel_store_reservation_orders(
            store_id="STR_x", store_name="가게", reason="픽업 마감",
        )
        assert (started, failed, total) == (0, 0, 0)
        enqueue_event_mock.assert_not_awaited()


    async def test_returns_zero_when_no_reservation_orders(
        self, service, order_repo_mock, enqueue_event_mock,
    ):
        order_repo_mock.get_store_current_orders_with_relations.return_value = [
            OrderFactory.create(status=OrderStatus.complete),
        ]
        started, failed, total = await service.cancel_store_reservation_orders(
            store_id="STR_x", store_name="가게", reason="픽업 마감",
        )
        assert (started, failed, total) == (0, 0, 0)
        enqueue_event_mock.assert_not_awaited()


    async def test_emits_refund_event_per_reservation_order(
        self, service, order_repo_mock, enqueue_event_mock,
    ):
        a = OrderFactory.create(status=OrderStatus.reservation, total_amount=10000)
        b = OrderFactory.create(status=OrderStatus.reservation, total_amount=15000)
        c = OrderFactory.create(status=OrderStatus.complete, total_amount=99999)
        order_repo_mock.get_store_current_orders_with_relations.return_value = [a, b, c]

        started, failed, total = await service.cancel_store_reservation_orders(
            store_id="STR_x", store_name="가게", reason="픽업 마감",
        )

        assert started == 2
        assert failed == 0
        assert total == 25000  # c (complete) 는 제외
        assert enqueue_event_mock.await_count == 2

        topics = [
            call.kwargs["topic"] for call in enqueue_event_mock.await_args_list
        ]
        assert topics == ["order.refund.requested", "order.refund.requested"]

        # payload v2 — store_name + customer_id 포함.
        first = enqueue_event_mock.await_args_list[0].kwargs["payload"]
        assert first["store_id"] == "STR_x"
        assert first["store_name"] == "가게"
        assert first["reason"] == "픽업 마감"
        assert "customer_id" in first


# ────────────────────────────────────────────────────────────────────
# refund_all_uncompleted — daily 미완료 환불 worker (Phase 5.3)
# ────────────────────────────────────────────────────────────────────

@pytest.mark.unit
class TestRefundAllUncompleted:

    async def test_returns_zero_when_no_uncompleted(
        self, service, order_repo_mock, enqueue_event_mock,
    ):
        order_repo_mock.get_all_orders_with_relations.return_value = [
            OrderFactory.create(status=OrderStatus.complete),
        ]
        started, failed, total = await service.refund_all_uncompleted()
        assert (started, failed, total) == (0, 0, 0)
        enqueue_event_mock.assert_not_awaited()


    async def test_skips_stores_without_payment_config(
        self, service, order_repo_mock, payment_client_mock, enqueue_event_mock,
    ):
        a = OrderFactory.create(
            status=OrderStatus.reservation, store_id="STR_noconfig",
            total_amount=10000,
        )
        order_repo_mock.get_all_orders_with_relations.return_value = [a]
        payment_client_mock.has_complete_info.return_value = False

        started, failed, total = await service.refund_all_uncompleted()
        assert started == 0
        assert failed == 1  # 1개 주문이 skip 됨
        assert total == 0
        enqueue_event_mock.assert_not_awaited()


    async def test_emits_event_for_each_eligible_order(
        self, service, order_repo_mock, payment_client_mock, enqueue_event_mock,
    ):
        a = OrderFactory.create(
            status=OrderStatus.reservation, store_id="STR_ok",
            total_amount=10000,
        )
        b = OrderFactory.create(
            status=OrderStatus.accept, store_id="STR_ok",
            total_amount=20000,
        )
        order_repo_mock.get_all_orders_with_relations.return_value = [a, b]
        payment_client_mock.has_complete_info.return_value = True

        started, failed, total = await service.refund_all_uncompleted()

        assert started == 2
        assert failed == 0
        assert total == 30000
        assert enqueue_event_mock.await_count == 2

        topics = [
            call.kwargs["topic"] for call in enqueue_event_mock.await_args_list
        ]
        assert topics == ["order.refund.requested", "order.refund.requested"]

        # payload v2 검증 — customer_id, store_name 포함.
        first = enqueue_event_mock.await_args_list[0].kwargs["payload"]
        assert first["store_id"] == "STR_ok"
        assert "store_name" in first
        assert "customer_id" in first
        assert first["reason"] == "영업 시간 종료로 인한 자동 환불"


# ────────────────────────────────────────────────────────────────────
# complete_store_accepted_orders — 마감 시간 worker
# ────────────────────────────────────────────────────────────────────

@pytest.mark.unit
class TestCompleteStoreAcceptedOrders:

    async def test_returns_zero_when_no_accepted(
        self, service, order_query_mock,
    ):
        order_query_mock.list_store_current_orders.return_value = [
            OrderFactory.create(status=OrderStatus.reservation),
        ]
        completed, failed = await service.complete_store_accepted_orders(
            store_id="STR_x", store_name="가게",
        )
        assert (completed, failed) == (0, 0)


    async def test_completes_all_accepted(
        self, service, order_query_mock, order_repo_mock,
    ):
        a = OrderFactory.create(status=OrderStatus.accept)
        b = OrderFactory.create(status=OrderStatus.accept)
        order_query_mock.list_store_current_orders.return_value = [a, b]
        order_repo_mock.complete_order.return_value = SimpleNamespace(status=OrderStatus.complete)

        completed, failed = await service.complete_store_accepted_orders(
            store_id="STR_x", store_name="가게",
        )

        assert completed == 2
        assert failed == 0
        assert order_repo_mock.complete_order.await_count == 2
