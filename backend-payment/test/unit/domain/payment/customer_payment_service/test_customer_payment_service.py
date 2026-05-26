"""Tests for ``app.domain.payment.service.customer_payment.CustomerPaymentService``.

MSA 분리 후 변경된 의존성:
  - seller 도메인 호출 → InternalSellerClient (HTTP)
  - order 도메인 호출 → InternalOrderClient (HTTP)
  - cart_items CRUD → CartItemService (local)
"""
from types import SimpleNamespace
import pytest
from datetime import datetime, timedelta, timezone

from app.domain.payment.service.exception import (
    BackendUnavailableError,
    OrderCreateFailedError,
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
from app.core.portone import PortOnePaymentStatus, PortOneTransientError

from test.unit.domain.payment.customer_payment_service.model_factory import (
    CartItemFactory,
    OperationInfoFactory,
    PaymentInfoFactory,
    ProductFactory,
)
from test.unit.domain.payment.customer_payment_service.mock_factory import (
    BackgroundTasksFakeFactory,
)


def _paid(amount: int) -> SimpleNamespace:
    return SimpleNamespace(
        status=PortOnePaymentStatus.PAID,
        total_amount=amount,
        payment_method="CARD",
    )


def _failed() -> SimpleNamespace:
    return SimpleNamespace(
        status=PortOnePaymentStatus.FAILED,
        total_amount=0,
        payment_method=None,
    )


# ────────────────────────────────────────────────────────────────────
# init_payment — backend HTTP 으로 product/stock 조회 + cart local 생성
# ────────────────────────────────────────────────────────────────────

@pytest.mark.unit
class TestInitPayment:

    async def test_raises_when_product_missing(self, service, seller_client_mock):
        seller_client_mock.find_product.return_value = None
        with pytest.raises(ProductNotFoundError):
            await service.init_payment(
                customer_email="alice@example.com", product_id="PRD_x", quantity=1,
            )


    async def test_raises_when_store_not_open(self, service, seller_client_mock):
        seller_client_mock.find_product.return_value = ProductFactory.create()
        seller_client_mock.get_today_operation.return_value = None
        with pytest.raises(StoreNotOpenError):
            await service.init_payment(
                customer_email="alice@example.com", product_id="PRD_x", quantity=1,
            )


    async def test_raises_when_store_currently_closed(self, service, seller_client_mock):
        seller_client_mock.find_product.return_value = ProductFactory.create()
        seller_client_mock.get_today_operation.return_value = OperationInfoFactory.closed()
        with pytest.raises(StoreNotOpenError):
            await service.init_payment(
                customer_email="alice@example.com", product_id="PRD_x", quantity=1,
            )


    async def test_raises_when_pickup_time_ended(self, service, seller_client_mock):
        seller_client_mock.find_product.return_value = ProductFactory.create()
        seller_client_mock.get_today_operation.return_value = OperationInfoFactory.pickup_ended()
        with pytest.raises(PickupTimeEndedError):
            await service.init_payment(
                customer_email="alice@example.com", product_id="PRD_x", quantity=1,
            )


    async def test_raises_when_stock_insufficient_pre_check(
        self, service, seller_client_mock,
    ):
        seller_client_mock.find_product.return_value = ProductFactory.create(
            current_stock=1,
        )
        seller_client_mock.get_today_operation.return_value = OperationInfoFactory.open()
        with pytest.raises(StockInsufficientError):
            await service.init_payment(
                customer_email="alice@example.com", product_id="PRD_x", quantity=5,
            )


    async def test_wraps_backend_stock_conflict(
        self, service, seller_client_mock, store_payment_info_mock,
    ):
        seller_client_mock.find_product.return_value = ProductFactory.create(
            current_stock=10,
        )
        seller_client_mock.get_today_operation.return_value = OperationInfoFactory.open()
        store_payment_info_mock.get_complete_by_store.return_value = (
            PaymentInfoFactory.create()
        )
        seller_client_mock.consume_stock.side_effect = StockConflictError("lock")
        with pytest.raises(StockConflictError):
            await service.init_payment(
                customer_email="alice@example.com", product_id="PRD_x", quantity=2,
            )


    async def test_wraps_backend_stock_insufficient(
        self, service, seller_client_mock, store_payment_info_mock,
    ):
        seller_client_mock.find_product.return_value = ProductFactory.create(
            current_stock=10,
        )
        seller_client_mock.get_today_operation.return_value = OperationInfoFactory.open()
        store_payment_info_mock.get_complete_by_store.return_value = (
            PaymentInfoFactory.create()
        )
        seller_client_mock.consume_stock.side_effect = StockInsufficientError("low")
        with pytest.raises(StockInsufficientError):
            await service.init_payment(
                customer_email="alice@example.com", product_id="PRD_x", quantity=2,
            )


    async def test_payment_info_missing_does_not_consume_stock(
        self,
        service,
        seller_client_mock,
        store_payment_info_mock,
        cart_item_service_mock,
    ):
        """payment_info 누락 시 stock 차감 전에 raise — fail-fast 순서 검증."""
        seller_client_mock.find_product.return_value = ProductFactory.create(
            current_stock=10,
        )
        seller_client_mock.get_today_operation.return_value = OperationInfoFactory.open()
        store_payment_info_mock.get_complete_by_store.side_effect = (
            PaymentInfoMissingError("missing")
        )

        with pytest.raises(PaymentInfoMissingError):
            await service.init_payment(
                customer_email="alice@example.com", product_id="PRD_x", quantity=2,
            )

        # stock 도 cart 도 손대지 않음.
        seller_client_mock.consume_stock.assert_not_awaited()
        cart_item_service_mock.create.assert_not_awaited()


    async def test_cart_create_failure_triggers_stock_compensation(
        self,
        service,
        seller_client_mock,
        store_payment_info_mock,
        cart_item_service_mock,
    ):
        """stock 차감 성공 + cart 생성 실패 → restore_stock 보상 호출."""
        seller_client_mock.find_product.return_value = ProductFactory.create(
            current_stock=10,
        )
        seller_client_mock.get_today_operation.return_value = OperationInfoFactory.open()
        store_payment_info_mock.get_complete_by_store.return_value = (
            PaymentInfoFactory.create()
        )
        cart_item_service_mock.create.side_effect = RuntimeError("db down")

        with pytest.raises(RuntimeError):
            await service.init_payment(
                customer_email="alice@example.com", product_id="PRD_x", quantity=2,
            )

        seller_client_mock.consume_stock.assert_awaited_once()
        seller_client_mock.restore_stock.assert_awaited_once()


    async def test_happy_path_creates_cart_with_expires_at(
        self,
        service,
        seller_client_mock,
        store_payment_info_mock,
        cart_item_service_mock,
    ):
        seller_client_mock.find_product.return_value = ProductFactory.create(
            current_stock=10, price=10000, sale=None,
        )
        seller_client_mock.get_today_operation.return_value = OperationInfoFactory.open()
        store_payment_info_mock.get_complete_by_store.return_value = (
            PaymentInfoFactory.create()
        )

        result = await service.init_payment(
            customer_email="alice@example.com", product_id="PRD_x", quantity=2,
        )

        # payment_id 가 consume + create 양쪽에 같은 값으로 전달됐는지.
        consume_kwargs = seller_client_mock.consume_stock.await_args.kwargs
        create_kwargs = cart_item_service_mock.create.await_args.kwargs
        assert consume_kwargs["payment_id"] == create_kwargs["payment_id"]
        assert consume_kwargs["product_id"] == "PRD_x"
        assert consume_kwargs["quantity"] == 2
        assert "expires_at" in create_kwargs

        assert result.quantity == 2
        assert result.price == 10000
        assert result.total_amount == 20000
        assert result.channel_id == "pc_x"
        assert result.store_id == "ps_x"
        assert result.payment_id.startswith("PAY_")


    async def test_applies_sale_with_hundred_won_rounding(
        self, service, seller_client_mock, store_payment_info_mock,
    ):
        seller_client_mock.find_product.return_value = ProductFactory.create(
            current_stock=10, price=10000, sale=15,
        )
        seller_client_mock.get_today_operation.return_value = OperationInfoFactory.open()
        store_payment_info_mock.get_complete_by_store.return_value = (
            PaymentInfoFactory.create()
        )

        result = await service.init_payment(
            customer_email="alice@example.com", product_id="PRD_x", quantity=1,
        )

        # 10000 * 0.85 = 8500. 100원 단위 올림 → 8500.
        assert result.total_amount == 8500


# ────────────────────────────────────────────────────────────────────
# confirm_payment + _finalize_payment
# ────────────────────────────────────────────────────────────────────

@pytest.mark.unit
class TestConfirmPayment:

    async def test_raises_timeout_when_cart_already_expired(
        self, service, cart_item_service_mock,
    ):
        expired_cart = CartItemFactory.create(
            customer_id="alice@example.com",
            expires_at=datetime.now(timezone.utc) - timedelta(seconds=1),
        )
        cart_item_service_mock.get.return_value = expired_cart
        bt, _ = BackgroundTasksFakeFactory.create()
        with pytest.raises(PaymentTimeoutError):
            await service.confirm_payment(
                customer_email="alice@example.com",
                payment_id=expired_cart.payment_id,
                background_tasks=bt,
            )


    async def test_raises_when_cart_missing(self, service, cart_item_service_mock):
        cart_item_service_mock.get.return_value = None
        bt, _ = BackgroundTasksFakeFactory.create()
        with pytest.raises(PaymentNotFoundError):
            await service.confirm_payment(
                customer_email="alice@example.com",
                payment_id="PAY_x",
                background_tasks=bt,
            )


    async def test_raises_when_cart_owner_mismatch(
        self, service, cart_item_service_mock,
    ):
        cart_item_service_mock.get.return_value = CartItemFactory.create(
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
        cart_item_service_mock,
        seller_client_mock,
        store_payment_info_mock,
        payment_gateway_mock,
    ):
        cart = CartItemFactory.create(
            customer_id="alice@example.com",
            product_id="PRD_x",
            quantity=2,
        )
        cart_item_service_mock.get.return_value = cart
        cart_item_service_mock.lock.return_value = cart
        seller_client_mock.find_product.return_value = ProductFactory.create()
        seller_client_mock.get_today_operation.return_value = OperationInfoFactory.open()
        store_payment_info_mock.get_complete_by_store.return_value = (
            PaymentInfoFactory.create()
        )
        payment_gateway_mock.verify.side_effect = PaymentVerificationError("PG mismatch")

        bt, _ = BackgroundTasksFakeFactory.create()
        with pytest.raises(PaymentVerificationError):
            await service.confirm_payment(
                customer_email="alice@example.com",
                payment_id="PAY_x",
                background_tasks=bt,
            )

        # verify 실패 — 돈 안 빠졌으므로 환불 시도 없음. restore + cart delete 호출됨.
        payment_gateway_mock.refund.assert_not_awaited()
        seller_client_mock.restore_stock.assert_awaited_once()
        cart_item_service_mock.delete.assert_awaited()


    async def test_happy_path_creates_order_and_schedules_email(
        self,
        service,
        cart_item_service_mock,
        seller_client_mock,
        store_payment_info_mock,
        payment_gateway_mock,
        order_client_mock,
    ):
        cart = CartItemFactory.create(customer_id="alice@example.com")
        cart_item_service_mock.get.return_value = cart
        cart_item_service_mock.lock.return_value = cart
        seller_client_mock.find_product.return_value = ProductFactory.create()
        seller_client_mock.get_today_operation.return_value = OperationInfoFactory.open()
        store_payment_info_mock.get_complete_by_store.return_value = (
            PaymentInfoFactory.create()
        )

        bt, tasks = BackgroundTasksFakeFactory.create()
        result = await service.confirm_payment(
            customer_email="alice@example.com",
            payment_id="PAY_x",
            background_tasks=bt,
        )

        payment_gateway_mock.verify.assert_awaited_once()
        order_client_mock.create_order_from_cart.assert_awaited_once()
        cart_item_service_mock.delete.assert_awaited_once_with("PAY_x")
        # 예약 완료 이메일 background task 등록.
        assert len(tasks) == 1
        assert result.payment_id == "PAY_x"


    async def test_returns_not_found_when_lock_finds_no_cart(
        self,
        service,
        cart_item_service_mock,
        seller_client_mock,
    ):
        cart_item_service_mock.get.return_value = CartItemFactory.create(
            customer_id="alice@example.com",
        )
        seller_client_mock.find_product.return_value = ProductFactory.create()
        seller_client_mock.get_today_operation.return_value = OperationInfoFactory.open()
        cart_item_service_mock.lock.return_value = None

        bt, _ = BackgroundTasksFakeFactory.create()
        with pytest.raises(PaymentNotFoundError):
            await service.confirm_payment(
                customer_email="alice@example.com",
                payment_id="PAY_x",
                background_tasks=bt,
            )


    async def test_order_create_4xx_triggers_refund(
        self,
        service,
        cart_item_service_mock,
        seller_client_mock,
        store_payment_info_mock,
        payment_gateway_mock,
        order_client_mock,
    ):
        """backend 가 4xx 로 명시적 거부 → 환불 + 보상 + raise."""
        cart = CartItemFactory.create(
            customer_id="alice@example.com", product_id="PRD_x", quantity=1,
        )
        cart_item_service_mock.get.return_value = cart
        cart_item_service_mock.lock.return_value = cart
        seller_client_mock.find_product.return_value = ProductFactory.create()
        seller_client_mock.get_today_operation.return_value = OperationInfoFactory.open()
        store_payment_info_mock.get_complete_by_store.return_value = (
            PaymentInfoFactory.create()
        )
        order_client_mock.create_order_from_cart.side_effect = OrderCreateFailedError(
            "rejected",
        )

        bt, _ = BackgroundTasksFakeFactory.create()
        with pytest.raises(OrderCreateFailedError):
            await service.confirm_payment(
                customer_email="alice@example.com",
                payment_id="PAY_x",
                background_tasks=bt,
            )

        payment_gateway_mock.refund.assert_awaited_once()
        seller_client_mock.restore_stock.assert_awaited_once()


    async def test_order_create_5xx_does_not_refund(
        self,
        service,
        cart_item_service_mock,
        seller_client_mock,
        store_payment_info_mock,
        payment_gateway_mock,
        order_client_mock,
    ):
        """backend 5xx → commit 여부 불명. 환불 금지, cart 유지, sweep 이 retry.

        regression: 5xx 시 환불해버리면 backend 가 실제 commit 된 주문이 외로워지는 사고.
        """
        cart = CartItemFactory.create(
            customer_id="alice@example.com", product_id="PRD_x", quantity=1,
        )
        cart_item_service_mock.get.return_value = cart
        cart_item_service_mock.lock.return_value = cart
        seller_client_mock.find_product.return_value = ProductFactory.create()
        seller_client_mock.get_today_operation.return_value = OperationInfoFactory.open()
        store_payment_info_mock.get_complete_by_store.return_value = (
            PaymentInfoFactory.create()
        )
        order_client_mock.create_order_from_cart.side_effect = BackendUnavailableError(
            "backend 503",
        )

        bt, _ = BackgroundTasksFakeFactory.create()
        with pytest.raises(BackendUnavailableError):
            await service.confirm_payment(
                customer_email="alice@example.com",
                payment_id="PAY_x",
                background_tasks=bt,
            )

        # 환불도, restore_stock 도, cart delete 도 호출되지 않아야 한다.
        payment_gateway_mock.refund.assert_not_awaited()
        seller_client_mock.restore_stock.assert_not_awaited()


# ────────────────────────────────────────────────────────────────────
# sweep_expired_carts
# ────────────────────────────────────────────────────────────────────

@pytest.mark.unit
class TestSweepExpiredCarts:

    async def test_returns_empty_when_nothing_expired(
        self, service, cart_item_service_mock, seller_client_mock,
    ):
        cart_item_service_mock.claim_expired_for_processing.return_value = []
        result = await service.sweep_expired_carts(limit=100)
        assert result.finalized == 0
        assert result.cancelled == 0
        assert result.transient == 0
        assert result.finalized_customer_emails == []
        seller_client_mock.restore_stock.assert_not_awaited()


    async def test_finalizes_paid_cart_and_collects_email(
        self,
        service,
        cart_item_service_mock,
        seller_client_mock,
        store_payment_info_mock,
        payment_gateway_mock,
        order_client_mock,
    ):
        cart = CartItemFactory.create(
            payment_id="PAY_paid",
            customer_id="alice@example.com",
            total_amount=10000,
        )
        cart_item_service_mock.claim_expired_for_processing.return_value = [cart]
        seller_client_mock.find_product.return_value = ProductFactory.create()
        store_payment_info_mock.get_complete_by_store.return_value = (
            PaymentInfoFactory.create()
        )
        payment_gateway_mock.fetch_status.return_value = _paid(10000)

        result = await service.sweep_expired_carts(limit=100)

        assert result.finalized == 1
        assert result.cancelled == 0
        assert result.finalized_customer_emails == ["alice@example.com"]
        order_client_mock.create_order_from_cart.assert_awaited_once()
        seller_client_mock.restore_stock.assert_not_awaited()


    async def test_cancels_when_portone_has_no_payment(
        self,
        service,
        cart_item_service_mock,
        seller_client_mock,
        store_payment_info_mock,
        payment_gateway_mock,
        order_client_mock,
    ):
        cart = CartItemFactory.create(
            payment_id="PAY_noshow", product_id="PRD_x", quantity=2,
        )
        cart_item_service_mock.claim_expired_for_processing.return_value = [cart]
        seller_client_mock.find_product.return_value = ProductFactory.create()
        store_payment_info_mock.get_complete_by_store.return_value = (
            PaymentInfoFactory.create()
        )
        payment_gateway_mock.fetch_status.return_value = None

        result = await service.sweep_expired_carts(limit=100)

        assert result.finalized == 0
        assert result.cancelled == 1
        seller_client_mock.restore_stock.assert_awaited_once()
        order_client_mock.create_order_from_cart.assert_not_awaited()


    async def test_cancels_when_payment_status_not_paid(
        self,
        service,
        cart_item_service_mock,
        seller_client_mock,
        store_payment_info_mock,
        payment_gateway_mock,
    ):
        cart = CartItemFactory.create(
            payment_id="PAY_failed", product_id="PRD_x", quantity=1,
        )
        cart_item_service_mock.claim_expired_for_processing.return_value = [cart]
        seller_client_mock.find_product.return_value = ProductFactory.create()
        store_payment_info_mock.get_complete_by_store.return_value = (
            PaymentInfoFactory.create()
        )
        payment_gateway_mock.fetch_status.return_value = _failed()

        result = await service.sweep_expired_carts(limit=100)

        assert result.cancelled == 1
        seller_client_mock.restore_stock.assert_awaited_once()


    async def test_cancels_when_paid_amount_mismatches(
        self,
        service,
        cart_item_service_mock,
        seller_client_mock,
        store_payment_info_mock,
        payment_gateway_mock,
        order_client_mock,
    ):
        cart = CartItemFactory.create(
            payment_id="PAY_tamper", product_id="PRD_x", quantity=1, total_amount=10000,
        )
        cart_item_service_mock.claim_expired_for_processing.return_value = [cart]
        seller_client_mock.find_product.return_value = ProductFactory.create()
        store_payment_info_mock.get_complete_by_store.return_value = (
            PaymentInfoFactory.create()
        )
        payment_gateway_mock.fetch_status.return_value = _paid(9999)

        result = await service.sweep_expired_carts(limit=100)

        assert result.cancelled == 1
        assert result.finalized == 0
        order_client_mock.create_order_from_cart.assert_not_awaited()
        seller_client_mock.restore_stock.assert_awaited_once()


    async def test_transient_portone_error_skips_cart(
        self,
        service,
        cart_item_service_mock,
        seller_client_mock,
        store_payment_info_mock,
        payment_gateway_mock,
        order_client_mock,
    ):
        cart = CartItemFactory.create(payment_id="PAY_5xx")
        cart_item_service_mock.claim_expired_for_processing.return_value = [cart]
        seller_client_mock.find_product.return_value = ProductFactory.create()
        store_payment_info_mock.get_complete_by_store.return_value = (
            PaymentInfoFactory.create()
        )
        payment_gateway_mock.fetch_status.side_effect = PortOneTransientError("502")

        result = await service.sweep_expired_carts(limit=100)

        assert result.transient == 1
        assert result.finalized == 0
        assert result.cancelled == 0
        order_client_mock.create_order_from_cart.assert_not_awaited()
        seller_client_mock.restore_stock.assert_not_awaited()


    async def test_backend_unavailable_skips_cart(
        self,
        service,
        cart_item_service_mock,
        seller_client_mock,
        store_payment_info_mock,
        payment_gateway_mock,
        order_client_mock,
    ):
        """is_paid 분기에서 backend 5xx 발생 — 다음 sweep 으로 미룸."""
        cart = CartItemFactory.create(
            payment_id="PAY_paid_backend_5xx",
            customer_id="alice@example.com",
            total_amount=10000,
        )
        cart_item_service_mock.claim_expired_for_processing.return_value = [cart]
        seller_client_mock.find_product.return_value = ProductFactory.create()
        store_payment_info_mock.get_complete_by_store.return_value = (
            PaymentInfoFactory.create()
        )
        payment_gateway_mock.fetch_status.return_value = _paid(10000)
        order_client_mock.create_order_from_cart.side_effect = BackendUnavailableError(
            "503",
        )

        result = await service.sweep_expired_carts(limit=100)

        assert result.transient == 1
        # 환불도 cart 삭제도 일어나지 않아야 한다.
        payment_gateway_mock.refund.assert_not_awaited()


    async def test_paid_but_backend_4xx_triggers_refund(
        self,
        service,
        cart_item_service_mock,
        seller_client_mock,
        store_payment_info_mock,
        payment_gateway_mock,
        order_client_mock,
    ):
        """PAID 인데 backend 가 명시적 거부 → 환불 + cancel."""
        cart = CartItemFactory.create(
            payment_id="PAY_paid_rejected",
            customer_id="alice@example.com",
            total_amount=10000,
        )
        cart_item_service_mock.claim_expired_for_processing.return_value = [cart]
        seller_client_mock.find_product.return_value = ProductFactory.create()
        store_payment_info_mock.get_complete_by_store.return_value = (
            PaymentInfoFactory.create()
        )
        payment_gateway_mock.fetch_status.return_value = _paid(10000)
        order_client_mock.create_order_from_cart.side_effect = OrderCreateFailedError(
            "rejected",
        )

        result = await service.sweep_expired_carts(limit=100)

        assert result.cancelled == 1
        payment_gateway_mock.refund.assert_awaited_once()


    async def test_payment_info_missing_treated_as_transient(
        self,
        service,
        cart_item_service_mock,
        seller_client_mock,
        store_payment_info_mock,
        payment_gateway_mock,
    ):
        cart = CartItemFactory.create(payment_id="PAY_noinfo")
        cart_item_service_mock.claim_expired_for_processing.return_value = [cart]
        seller_client_mock.find_product.return_value = ProductFactory.create()
        store_payment_info_mock.get_complete_by_store.side_effect = (
            PaymentInfoMissingError("gone")
        )

        result = await service.sweep_expired_carts(limit=100)

        assert result.transient == 1
        payment_gateway_mock.fetch_status.assert_not_awaited()


    async def test_mixed_batch_isolated_outcomes(
        self,
        service,
        cart_item_service_mock,
        seller_client_mock,
        store_payment_info_mock,
        payment_gateway_mock,
    ):
        paid_cart = CartItemFactory.create(
            payment_id="PAY_paid", customer_id="alice@example.com", total_amount=10000,
        )
        noshow_cart = CartItemFactory.create(payment_id="PAY_noshow")
        transient_cart = CartItemFactory.create(payment_id="PAY_5xx")
        cart_item_service_mock.claim_expired_for_processing.return_value = [
            paid_cart, noshow_cart, transient_cart,
        ]
        seller_client_mock.find_product.return_value = ProductFactory.create()
        store_payment_info_mock.get_complete_by_store.return_value = (
            PaymentInfoFactory.create()
        )

        payment_gateway_mock.fetch_status.side_effect = [
            _paid(10000),
            None,
            PortOneTransientError("503"),
        ]

        result = await service.sweep_expired_carts(limit=100)

        assert result.finalized == 1
        assert result.cancelled == 1
        assert result.transient == 1
        assert result.finalized_customer_emails == ["alice@example.com"]
