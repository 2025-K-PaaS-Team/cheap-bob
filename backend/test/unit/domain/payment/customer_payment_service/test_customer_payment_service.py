"""Tests for ``app.domain.payment.service.customer_payment.CustomerPaymentService``."""
import pytest

from app.domain.payment.service.exception import (
    PaymentInfoIncompleteError,
    PaymentInfoMissingError,
    PaymentNotFoundError,
    PaymentOwnershipMismatchError,
    PaymentTimeoutError,
    PaymentVerificationError,
    PickupTimeEndedError,
    ProductNotFoundError,
    StockConflictError,
    StockInsufficientError,
    StoreNotOpenError,
)
from app.domain.seller.service.exception import (
    ProductStockConflictError,
    ProductStockInsufficientError,
)

from test.unit.domain.payment.customer_payment_service.model_factory import (
    CartItemFactory,
    OperationInfoFactory,
    PaymentInfoFactory,
    ProductFactory,
)
from test.unit.domain.payment.customer_payment_service.mock_factory import (
    BackgroundTasksFakeFactory,
)


# ────────────────────────────────────────────────────────────────────
# init_payment
# ────────────────────────────────────────────────────────────────────

@pytest.mark.unit
class TestInitPayment:

    async def test_raises_when_product_missing(self, service, product_service_mock):
        product_service_mock.find_product.return_value = None
        with pytest.raises(ProductNotFoundError):
            await service.init_payment(
                customer_email="alice@example.com", product_id="PRD_x", quantity=1,
            )


    async def test_raises_when_store_not_open(
        self, service, product_service_mock, store_read_mock,
    ):
        product_service_mock.find_product.return_value = ProductFactory.create()
        store_read_mock.get_today_operation.return_value = None
        with pytest.raises(StoreNotOpenError):
            await service.init_payment(
                customer_email="alice@example.com", product_id="PRD_x", quantity=1,
            )


    async def test_raises_when_store_currently_closed(
        self, service, product_service_mock, store_read_mock,
    ):
        product_service_mock.find_product.return_value = ProductFactory.create()
        store_read_mock.get_today_operation.return_value = OperationInfoFactory.closed()
        with pytest.raises(StoreNotOpenError):
            await service.init_payment(
                customer_email="alice@example.com", product_id="PRD_x", quantity=1,
            )


    async def test_raises_when_pickup_time_ended(
        self, service, product_service_mock, store_read_mock,
    ):
        product_service_mock.find_product.return_value = ProductFactory.create()
        store_read_mock.get_today_operation.return_value = OperationInfoFactory.pickup_ended()
        with pytest.raises(PickupTimeEndedError):
            await service.init_payment(
                customer_email="alice@example.com", product_id="PRD_x", quantity=1,
            )


    async def test_raises_when_stock_insufficient_pre_check(
        self, service, product_service_mock, store_read_mock,
    ):
        product_service_mock.find_product.return_value = ProductFactory.create(
            current_stock=1,
        )
        store_read_mock.get_today_operation.return_value = OperationInfoFactory.open()
        with pytest.raises(StockInsufficientError):
            await service.init_payment(
                customer_email="alice@example.com", product_id="PRD_x", quantity=5,
            )


    async def test_wraps_repo_stock_conflict_to_stock_conflict_error(
        self, service, product_service_mock, store_read_mock,
    ):
        product_service_mock.find_product.return_value = ProductFactory.create(
            current_stock=10,
        )
        store_read_mock.get_today_operation.return_value = OperationInfoFactory.open()
        product_service_mock.consume_purchased_stock.side_effect = ProductStockConflictError("lock")
        with pytest.raises(StockConflictError):
            await service.init_payment(
                customer_email="alice@example.com", product_id="PRD_x", quantity=2,
            )


    async def test_wraps_repo_stock_insufficient(
        self, service, product_service_mock, store_read_mock,
    ):
        product_service_mock.find_product.return_value = ProductFactory.create(
            current_stock=10,
        )
        store_read_mock.get_today_operation.return_value = OperationInfoFactory.open()
        product_service_mock.consume_purchased_stock.side_effect = ProductStockInsufficientError("low")
        with pytest.raises(StockInsufficientError):
            await service.init_payment(
                customer_email="alice@example.com", product_id="PRD_x", quantity=2,
            )


    async def test_restores_stock_when_payment_info_missing(
        self,
        service,
        product_service_mock,
        store_read_mock,
        store_payment_info_mock,
    ):
        product_service_mock.find_product.return_value = ProductFactory.create(
            current_stock=10,
        )
        store_read_mock.get_today_operation.return_value = OperationInfoFactory.open()
        store_payment_info_mock.get_complete_by_store.side_effect = (
            PaymentInfoMissingError("missing")
        )

        with pytest.raises(PaymentInfoMissingError):
            await service.init_payment(
                customer_email="alice@example.com", product_id="PRD_x", quantity=2,
            )

        # 차감했던 재고는 되돌려놔야 한다.
        product_service_mock.restore_purchased_stock.assert_awaited_once_with(
            product_id="PRD_x", quantity=2,
        )


    async def test_happy_path_creates_cart_and_schedules_timeout(
        self,
        service,
        product_service_mock,
        store_read_mock,
        store_payment_info_mock,
        payment_scheduler_mock,
        order_query_mock,
    ):
        product_service_mock.find_product.return_value = ProductFactory.create(
            current_stock=10, price=10000, sale=None,
        )
        store_read_mock.get_today_operation.return_value = OperationInfoFactory.open()
        store_payment_info_mock.get_complete_by_store.return_value = (
            PaymentInfoFactory.create()
        )

        result = await service.init_payment(
            customer_email="alice@example.com", product_id="PRD_x", quantity=2,
        )

        product_service_mock.consume_purchased_stock.assert_awaited_once_with(
            product_id="PRD_x", quantity=2,
        )
        payment_scheduler_mock.schedule_payment_timeout.assert_awaited_once()
        order_query_mock.create_cart_item.assert_awaited_once()

        assert result.quantity == 2
        assert result.price == 10000
        assert result.total_amount == 20000
        assert result.channel_id == "pc_x"
        assert result.store_id == "ps_x"
        assert result.payment_id.startswith("PAY_")


    async def test_applies_sale_with_hundred_won_rounding(
        self,
        service,
        product_service_mock,
        store_read_mock,
        store_payment_info_mock,
    ):
        """sale 적용 시 단위가 100원 단위로 올림 처리되는지."""
        product_service_mock.find_product.return_value = ProductFactory.create(
            current_stock=10, price=10000, sale=15,  # 8500 -> 8500
        )
        store_read_mock.get_today_operation.return_value = OperationInfoFactory.open()
        store_payment_info_mock.get_complete_by_store.return_value = (
            PaymentInfoFactory.create()
        )

        result = await service.init_payment(
            customer_email="alice@example.com", product_id="PRD_x", quantity=1,
        )

        # 10000 * 0.85 = 8500. 100원 단위 올림 → 8500.
        assert result.total_amount == 8500


# ────────────────────────────────────────────────────────────────────
# confirm_payment
# ────────────────────────────────────────────────────────────────────

@pytest.mark.unit
class TestConfirmPayment:

    async def test_raises_timeout_when_schedule_already_removed(
        self, service, payment_scheduler_mock,
    ):
        payment_scheduler_mock.remove_payment_schedule.return_value = False
        bt, _ = BackgroundTasksFakeFactory.create()
        with pytest.raises(PaymentTimeoutError):
            await service.confirm_payment(
                customer_email="alice@example.com",
                payment_id="PAY_x",
                background_tasks=bt,
            )


    async def test_raises_when_cart_missing(
        self, service, order_query_mock,
    ):
        order_query_mock.get_cart_item.return_value = None
        bt, _ = BackgroundTasksFakeFactory.create()
        with pytest.raises(PaymentNotFoundError):
            await service.confirm_payment(
                customer_email="alice@example.com",
                payment_id="PAY_x",
                background_tasks=bt,
            )


    async def test_raises_when_cart_owner_mismatch(
        self, service, order_query_mock,
    ):
        order_query_mock.get_cart_item.return_value = CartItemFactory.create(
            customer_id="other@example.com",
        )
        bt, _ = BackgroundTasksFakeFactory.create()
        with pytest.raises(PaymentOwnershipMismatchError):
            await service.confirm_payment(
                customer_email="alice@example.com",
                payment_id="PAY_x",
                background_tasks=bt,
            )


    async def test_rolls_back_when_verification_fails(
        self,
        service,
        order_query_mock,
        product_service_mock,
        store_read_mock,
        store_payment_info_mock,
        payment_gateway_mock,
    ):
        order_query_mock.get_cart_item.return_value = CartItemFactory.create(
            customer_id="alice@example.com",
            product_id="PRD_x",
            quantity=2,
        )
        product_service_mock.find_product.return_value = ProductFactory.create()
        store_read_mock.get_today_operation.return_value = OperationInfoFactory.open()
        store_payment_info_mock.get_by_store.return_value = PaymentInfoFactory.create()
        payment_gateway_mock.verify.side_effect = PaymentVerificationError("PG mismatch")

        bt, _ = BackgroundTasksFakeFactory.create()
        with pytest.raises(PaymentVerificationError):
            await service.confirm_payment(
                customer_email="alice@example.com",
                payment_id="PAY_x",
                background_tasks=bt,
            )

        # 롤백 — 환불 시도 + 재고 복구 + cart 삭제.
        payment_gateway_mock.refund.assert_awaited_once()
        product_service_mock.restore_purchased_stock.assert_awaited_once_with(
            product_id="PRD_x", quantity=2,
        )
        order_query_mock.delete_cart_item.assert_awaited()


    async def test_happy_path_creates_order_and_schedules_email(
        self,
        service,
        order_query_mock,
        product_service_mock,
        store_read_mock,
        store_payment_info_mock,
        payment_gateway_mock,
    ):
        order_query_mock.get_cart_item.return_value = CartItemFactory.create(
            customer_id="alice@example.com",
        )
        product_service_mock.find_product.return_value = ProductFactory.create()
        store_read_mock.get_today_operation.return_value = OperationInfoFactory.open()
        store_payment_info_mock.get_by_store.return_value = PaymentInfoFactory.create()

        bt, tasks = BackgroundTasksFakeFactory.create()
        result = await service.confirm_payment(
            customer_email="alice@example.com",
            payment_id="PAY_x",
            background_tasks=bt,
        )

        payment_gateway_mock.verify.assert_awaited_once()
        order_query_mock.create_order_from_cart.assert_awaited_once()
        order_query_mock.delete_cart_item.assert_awaited_once_with("PAY_x")
        # 예약 완료 이메일 background task 등록.
        assert len(tasks) == 1
        assert result.payment_id == "PAY_x"
