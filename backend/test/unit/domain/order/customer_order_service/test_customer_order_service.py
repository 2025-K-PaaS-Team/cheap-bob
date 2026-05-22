"""Tests for ``app.domain.order.service.customer_order.CustomerOrderService``."""
from unittest.mock import patch
from types import SimpleNamespace
from test.unit.domain.order.customer_order_service.model_factory import (
    OrderFactory,
    OrderHistoryFactory,
)
from test.unit.domain.order.customer_order_service.mock_factory import BackgroundTasksFakeFactory
import pytest
from datetime import datetime, timedelta, timezone

from app.domain.payment.service.exception import (
    PaymentInfoMissingError,
    PaymentRefundError,
)
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
from app.domain.order.dto.order import OrderStatus


# ────────────────────────────────────────────────────────────────────
# list_orders — current + history 머지 + 시간 desc 정렬
# ────────────────────────────────────────────────────────────────────

@pytest.mark.unit
class TestListOrders:

    async def test_returns_empty_when_no_orders(
        self, service, order_repo_mock, history_repo_mock, store_image_mock,
    ):
        order_repo_mock.get_customer_current_orders.return_value = []
        history_repo_mock.get_customer_history.return_value = []

        result = await service.list_orders("alice@example.com")

        assert result.total == 0
        assert result.orders == []


    async def test_merges_current_and_history(
        self, service, order_repo_mock, history_repo_mock, store_image_mock,
    ):
        current = [OrderFactory.create(customer_id="alice@example.com")]
        history = [OrderHistoryFactory.create(customer_id="alice@example.com")]
        order_repo_mock.get_customer_current_orders.return_value = current
        history_repo_mock.get_customer_history.return_value = history
        store_image_mock.get_main_image_urls.return_value = {
            history[0].store_id: "https://cdn/store.jpg",
        }

        result = await service.list_orders("alice@example.com")

        assert result.total == 2
        # main_image_url 은 history 응답에만 결합.
        history_resp = next(o for o in result.orders if o.store_id == history[0].store_id)
        assert history_resp.main_image_url == "https://cdn/store.jpg"


# ────────────────────────────────────────────────────────────────────
# get_detail
# ────────────────────────────────────────────────────────────────────

@pytest.mark.unit
class TestGetDetail:

    async def test_raises_when_not_found(self, service, order_repo_mock):
        order_repo_mock.get_order_with_relations.return_value = None
        with pytest.raises(OrderNotFoundError):
            await service.get_detail(
                customer_email="customer@example.com", payment_id="PAY_missing",
            )


    async def test_returns_response_when_found(self, service, order_repo_mock):
        order = OrderFactory.create(
            payment_id="PAY_x", customer_id="customer@example.com",
        )
        order_repo_mock.get_order_with_relations.return_value = order

        result = await service.get_detail(
            customer_email="customer@example.com", payment_id="PAY_x",
        )

        assert result.payment_id == "PAY_x"
        assert result.status == order.status


# ────────────────────────────────────────────────────────────────────
# complete_pickup — QR + 3-way 일치 검증
# ────────────────────────────────────────────────────────────────────

@pytest.mark.unit
class TestCompletePickup:

    async def test_raises_when_order_not_found(self, service, order_repo_mock):
        order_repo_mock.get_order_with_relations.return_value = None
        with pytest.raises(OrderNotFoundError):
            await service.complete_pickup(
                customer_email="alice@example.com",
                payment_id="PAY_x",
                qr_data="QR_anything",
            )


    async def test_raises_when_already_completed(self, service, order_repo_mock):
        order = OrderFactory.create(
            status=OrderStatus.complete, customer_id="alice@example.com",
        )
        order_repo_mock.get_order_with_relations.return_value = order
        with pytest.raises(OrderAlreadyCompletedError):
            await service.complete_pickup(
                customer_email="alice@example.com",
                payment_id=order.payment_id,
                qr_data="QR",
            )


    async def test_raises_when_not_accepted(self, service, order_repo_mock):
        order = OrderFactory.create(
            status=OrderStatus.reservation, customer_id="alice@example.com",
        )
        order_repo_mock.get_order_with_relations.return_value = order
        with pytest.raises(OrderNotAcceptedError):
            await service.complete_pickup(
                customer_email="alice@example.com",
                payment_id=order.payment_id,
                qr_data="QR",
            )


    async def test_raises_when_qr_invalid(self, service, order_repo_mock):
        # ownership 은 통과시키고 QR 검증 단계에서 실패하는 것을 확인.
        order = OrderFactory.create(
            status=OrderStatus.accept, customer_id="alice@example.com",
        )
        order_repo_mock.get_order_with_relations.return_value = order

        # validate_qr_data 가 호출되며 invalid QR 은 (False, None, "msg") 반환.
        with patch(
            "app.domain.order.service.customer_order.validate_qr_data",
            return_value=(False, None, "유효하지 않은 QR"),
        ):
            with pytest.raises(OrderQrInvalidError):
                await service.complete_pickup(
                    customer_email="alice@example.com",
                    payment_id=order.payment_id,
                    qr_data="QR_bad",
                )


    async def test_raises_when_qr_customer_mismatch(self, service, order_repo_mock):
        order = OrderFactory.create(
            status=OrderStatus.accept,
            customer_id="alice@example.com",
            product_id="PRD_x",
            payment_id="PAY_x",
        )
        order_repo_mock.get_order_with_relations.return_value = order

        # QR 의 customer_id 가 JWT customer 와 일치하지 않는 케이스.
        with patch(
            "app.domain.order.service.customer_order.validate_qr_data",
            return_value=(True, {
                "customer_id": "OTHER@example.com",
                "payment_id": "PAY_x",
                "product_id": "PRD_x",
            }, None),
        ):
            with pytest.raises(OrderOwnershipMismatchError):
                await service.complete_pickup(
                    customer_email="alice@example.com",
                    payment_id="PAY_x",
                    qr_data="QR_ok",
                )


    async def test_completes_order_on_success(self, service, order_repo_mock):
        order = OrderFactory.create(
            status=OrderStatus.accept,
            customer_id="alice@example.com",
            product_id="PRD_x",
            payment_id="PAY_x",
        )
        order_repo_mock.get_order_with_relations.return_value = order
        completed = SimpleNamespace(
            status=OrderStatus.complete,
            completed_at=datetime.now(timezone.utc),
        )
        order_repo_mock.complete_order.return_value = completed

        with patch(
            "app.domain.order.service.customer_order.validate_qr_data",
            return_value=(True, {
                "customer_id": "alice@example.com",
                "payment_id": "PAY_x",
                "product_id": "PRD_x",
            }, None),
        ):
            result = await service.complete_pickup(
                customer_email="alice@example.com",
                payment_id="PAY_x",
                qr_data="QR_ok",
            )

        order_repo_mock.complete_order.assert_awaited_once_with("PAY_x")
        assert result.status == OrderStatus.complete


# ────────────────────────────────────────────────────────────────────
# cancel
# ────────────────────────────────────────────────────────────────────

@pytest.mark.unit
class TestCancel:

    async def test_raises_when_order_not_found(self, service, order_repo_mock):
        order_repo_mock.get_order_with_relations.return_value = None
        bt, _ = BackgroundTasksFakeFactory.create()
        with pytest.raises(OrderNotFoundError):
            await service.cancel(
                customer_email="alice@example.com",
                payment_id="PAY_x",
                reason="단순 변심",
                background_tasks=bt,
            )


    async def test_raises_when_already_canceled(self, service, order_repo_mock):
        order = OrderFactory.create(
            status=OrderStatus.cancel, customer_id="alice@example.com",
        )
        order_repo_mock.get_order_with_relations.return_value = order
        bt, _ = BackgroundTasksFakeFactory.create()
        with pytest.raises(OrderAlreadyCanceledError):
            await service.cancel(
                customer_email="alice@example.com",
                payment_id=order.payment_id,
                reason="단순 변심",
                background_tasks=bt,
            )


    async def test_raises_when_already_accepted(self, service, order_repo_mock):
        """customer 는 accept/complete 된 주문을 취소할 수 없다."""
        order = OrderFactory.create(
            status=OrderStatus.accept, customer_id="alice@example.com",
        )
        order_repo_mock.get_order_with_relations.return_value = order
        bt, _ = BackgroundTasksFakeFactory.create()
        with pytest.raises(OrderNotInReservationError):
            await service.cancel(
                customer_email="alice@example.com",
                payment_id=order.payment_id,
                reason="단순 변심",
                background_tasks=bt,
            )


    async def test_raises_refund_error_when_payment_info_missing(
        self, service, order_repo_mock, store_payment_info_mock,
    ):
        order = OrderFactory.create(
            status=OrderStatus.reservation, customer_id="alice@example.com",
        )
        order_repo_mock.get_order_with_relations.return_value = order
        store_payment_info_mock.get_complete_by_store.side_effect = (
            PaymentInfoMissingError("payment info missing")
        )
        bt, _ = BackgroundTasksFakeFactory.create()
        with pytest.raises(OrderRefundError):
            await service.cancel(
                customer_email="alice@example.com",
                payment_id=order.payment_id,
                reason="단순 변심",
                background_tasks=bt,
            )


    async def test_raises_refund_error_when_portone_refund_fails(
        self, service, order_repo_mock, payment_gateway_mock,
    ):
        order = OrderFactory.create(
            status=OrderStatus.reservation, customer_id="alice@example.com",
        )
        order_repo_mock.get_order_with_relations.return_value = order
        payment_gateway_mock.refund.side_effect = PaymentRefundError("network err")
        bt, _ = BackgroundTasksFakeFactory.create()
        with pytest.raises(OrderRefundError):
            await service.cancel(
                customer_email="alice@example.com",
                payment_id=order.payment_id,
                reason="단순 변심",
                background_tasks=bt,
            )


    async def test_refunds_restores_stock_and_schedules_email(
        self,
        service,
        order_repo_mock,
        payment_gateway_mock,
        product_service_mock,
        store_read_mock,
    ):
        order = OrderFactory.create(
            status=OrderStatus.reservation,
            customer_id="alice@example.com",
            quantity=3,
            total_amount=30000,
        )
        order_repo_mock.get_order_with_relations.return_value = order
        order_repo_mock.cancel_order.return_value = 3
        store_read_mock.get_with_full_info.return_value = SimpleNamespace(store_name="가게")

        bt, tasks = BackgroundTasksFakeFactory.create()
        result = await service.cancel(
            customer_email="alice@example.com",
            payment_id=order.payment_id,
            reason="단순 변심",
            background_tasks=bt,
        )

        payment_gateway_mock.refund.assert_awaited_once()
        product_service_mock.restore_purchased_stock.assert_awaited_once_with(
            product_id=order.product_id, quantity=3,
        )
        # 이메일 발송 background task 가 등록됐는지 확인.
        assert len(tasks) == 1
        assert result.payment_id == order.payment_id
        assert result.quantity == 3
        assert result.total_amount == 30000
