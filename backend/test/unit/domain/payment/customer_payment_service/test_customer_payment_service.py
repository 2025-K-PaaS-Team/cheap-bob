"""Tests for ``app.domain.payment.service.customer_payment.CustomerPaymentService``."""
from types import SimpleNamespace
import pytest
from datetime import datetime, timedelta, timezone

from app.domain.seller.service.exception import (
    ProductStockConflictError,
    ProductStockInsufficientError,
)
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
from app.core.portone import PortOnePaymentStatus, PortOneTransientError


def _paid(amount: int) -> SimpleNamespace:
    """``fetch_status`` 가 반환하는 PortOnePayment-like 객체 — PAID."""
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


    async def test_payment_info_missing_rolls_back_consume(
        self,
        service,
        product_service_mock,
        store_read_mock,
        store_payment_info_mock,
        order_query_mock,
    ):
        """payment_info 조회 실패 시 raise — ``@transactional`` 이 outer tx 를 롤백해
        차감된 재고를 자동 복원한다. 명시적 restore_purchased_stock 호출은 없다."""
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

        # 재고 차감은 시도됐다 (실제 commit 은 outer tx 롤백으로 무효화됨).
        product_service_mock.consume_purchased_stock.assert_awaited_once_with(
            product_id="PRD_x", quantity=2,
        )
        # cart 는 생성되지 않았다.
        order_query_mock.create_cart_item.assert_not_awaited()
        # 명시적 restore 호출 없음 — 롤백이 책임진다.
        product_service_mock.restore_purchased_stock.assert_not_awaited()


    async def test_happy_path_creates_cart_with_expires_at(
        self,
        service,
        product_service_mock,
        store_read_mock,
        store_payment_info_mock,
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
        order_query_mock.create_cart_item.assert_awaited_once()
        # expires_at 이 약 5분 뒤로 설정됐는지.
        kwargs = order_query_mock.create_cart_item.await_args.kwargs
        assert "expires_at" in kwargs

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

    async def test_raises_timeout_when_cart_already_expired(
        self, service, order_query_mock,
    ):
        # cart 는 존재하지만 expires_at 이 이미 지난 경우 — sweeper 가 아직 정리 전.
        expired_cart = CartItemFactory.create(
            customer_id="alice@example.com",
            expires_at=datetime.now(timezone.utc) - timedelta(seconds=1),
        )
        order_query_mock.get_cart_item.return_value = expired_cart
        bt, _ = BackgroundTasksFakeFactory.create()
        with pytest.raises(PaymentTimeoutError):
            await service.confirm_payment(
                customer_email="alice@example.com",
                payment_id=expired_cart.payment_id,
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
        cart = CartItemFactory.create(
            customer_id="alice@example.com",
            product_id="PRD_x",
            quantity=2,
        )
        # confirm 사전 검증 + _finalize_payment 의 lock_cart_item 둘 다 같은 cart 반환.
        order_query_mock.get_cart_item.return_value = cart
        order_query_mock.lock_cart_item.return_value = cart
        product_service_mock.find_product.return_value = ProductFactory.create()
        store_read_mock.get_today_operation.return_value = OperationInfoFactory.open()
        store_payment_info_mock.get_complete_by_store.return_value = PaymentInfoFactory.create()
        payment_gateway_mock.verify.side_effect = PaymentVerificationError("PG mismatch")

        bt, _ = BackgroundTasksFakeFactory.create()
        with pytest.raises(PaymentVerificationError):
            await service.confirm_payment(
                customer_email="alice@example.com",
                payment_id="PAY_x",
                background_tasks=bt,
            )

        # verify 실패 — 돈 안 빠졌으므로 환불 시도 없음. 재고 복구 + cart 삭제만.
        payment_gateway_mock.refund.assert_not_awaited()
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
        cart = CartItemFactory.create(customer_id="alice@example.com")
        order_query_mock.get_cart_item.return_value = cart
        order_query_mock.lock_cart_item.return_value = cart
        product_service_mock.find_product.return_value = ProductFactory.create()
        store_read_mock.get_today_operation.return_value = OperationInfoFactory.open()
        store_payment_info_mock.get_complete_by_store.return_value = PaymentInfoFactory.create()

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


    async def test_returns_not_found_when_lock_finds_no_cart(
        self, service, order_query_mock, product_service_mock, store_read_mock,
    ):
        """사전 검증은 통과했지만 lock 시점에 cart 가 사라진 경우 (다른 흐름이 먼저 처리)."""
        order_query_mock.get_cart_item.return_value = CartItemFactory.create(
            customer_id="alice@example.com",
        )
        product_service_mock.find_product.return_value = ProductFactory.create()
        store_read_mock.get_today_operation.return_value = OperationInfoFactory.open()
        order_query_mock.lock_cart_item.return_value = None  # ← race 발생

        bt, _ = BackgroundTasksFakeFactory.create()
        with pytest.raises(PaymentNotFoundError):
            await service.confirm_payment(
                customer_email="alice@example.com",
                payment_id="PAY_x",
                background_tasks=bt,
            )


# ────────────────────────────────────────────────────────────────────
# sweep_expired_carts (만료 cart sweeper — confirm 누락 안전망)
# ────────────────────────────────────────────────────────────────────

@pytest.mark.unit
class TestSweepExpiredCarts:

    async def test_returns_empty_result_when_nothing_expired(
        self, service, cart_repo_mock, product_service_mock,
    ):
        cart_repo_mock.claim_expired_for_processing.return_value = []
        result = await service.sweep_expired_carts(limit=100)
        assert result.finalized == 0
        assert result.cancelled == 0
        assert result.transient == 0
        assert result.finalized_customer_emails == []
        product_service_mock.restore_purchased_stock.assert_not_awaited()


    async def test_finalizes_paid_cart_and_collects_email(
        self,
        service,
        cart_repo_mock,
        product_service_mock,
        store_payment_info_mock,
        payment_gateway_mock,
        order_query_mock,
    ):
        """결제는 됐는데 confirm 안 옴 — sweeper 가 주문 자동 생성."""
        cart = CartItemFactory.create(
            payment_id="PAY_paid",
            customer_id="alice@example.com",
            total_amount=10000,
        )
        cart_repo_mock.claim_expired_for_processing.return_value = [cart]
        product_service_mock.find_product.return_value = ProductFactory.create()
        store_payment_info_mock.get_complete_by_store.return_value = PaymentInfoFactory.create()
        payment_gateway_mock.fetch_status.return_value = _paid(10000)

        result = await service.sweep_expired_carts(limit=100)

        assert result.finalized == 1
        assert result.cancelled == 0
        assert result.finalized_customer_emails == ["alice@example.com"]
        order_query_mock.create_order_from_cart.assert_awaited_once()
        # finalize 분기 — 재고 복구는 없다 (주문이 그대로 살아있어야 하므로).
        product_service_mock.restore_purchased_stock.assert_not_awaited()


    async def test_cancels_when_portone_has_no_payment(
        self,
        service,
        cart_repo_mock,
        product_service_mock,
        store_payment_info_mock,
        payment_gateway_mock,
        order_query_mock,
    ):
        """사용자가 결제창을 그대로 닫음 — PortOne 측 기록 없음 → 재고 복구 + cart 삭제."""
        cart = CartItemFactory.create(
            payment_id="PAY_noshow", product_id="PRD_x", quantity=2,
        )
        cart_repo_mock.claim_expired_for_processing.return_value = [cart]
        product_service_mock.find_product.return_value = ProductFactory.create()
        store_payment_info_mock.get_complete_by_store.return_value = PaymentInfoFactory.create()
        payment_gateway_mock.fetch_status.return_value = None  # NotFound

        result = await service.sweep_expired_carts(limit=100)

        assert result.finalized == 0
        assert result.cancelled == 1
        product_service_mock.restore_purchased_stock.assert_awaited_once_with(
            product_id="PRD_x", quantity=2,
        )
        order_query_mock.create_order_from_cart.assert_not_awaited()


    async def test_cancels_when_payment_status_not_paid(
        self,
        service,
        cart_repo_mock,
        product_service_mock,
        store_payment_info_mock,
        payment_gateway_mock,
    ):
        cart = CartItemFactory.create(
            payment_id="PAY_failed", product_id="PRD_x", quantity=1,
        )
        cart_repo_mock.claim_expired_for_processing.return_value = [cart]
        product_service_mock.find_product.return_value = ProductFactory.create()
        store_payment_info_mock.get_complete_by_store.return_value = PaymentInfoFactory.create()
        payment_gateway_mock.fetch_status.return_value = _failed()

        result = await service.sweep_expired_carts(limit=100)

        assert result.cancelled == 1
        product_service_mock.restore_purchased_stock.assert_awaited_once()


    async def test_cancels_when_paid_amount_mismatches(
        self,
        service,
        cart_repo_mock,
        product_service_mock,
        store_payment_info_mock,
        payment_gateway_mock,
        order_query_mock,
    ):
        """PAID 인데 금액이 cart 와 다른 케이스 — tampering 가능성. 정리하고 CRITICAL 로깅."""
        cart = CartItemFactory.create(
            payment_id="PAY_tamper", product_id="PRD_x", quantity=1, total_amount=10000,
        )
        cart_repo_mock.claim_expired_for_processing.return_value = [cart]
        product_service_mock.find_product.return_value = ProductFactory.create()
        store_payment_info_mock.get_complete_by_store.return_value = PaymentInfoFactory.create()
        payment_gateway_mock.fetch_status.return_value = _paid(9999)  # 금액 다름

        result = await service.sweep_expired_carts(limit=100)

        assert result.cancelled == 1
        assert result.finalized == 0
        order_query_mock.create_order_from_cart.assert_not_awaited()
        product_service_mock.restore_purchased_stock.assert_awaited_once()


    async def test_transient_portone_error_skips_cart(
        self,
        service,
        cart_repo_mock,
        product_service_mock,
        store_payment_info_mock,
        payment_gateway_mock,
        order_query_mock,
    ):
        """PortOne 5xx — 다음 sweep 으로 미룸. cart 손대지 않음."""
        cart = CartItemFactory.create(payment_id="PAY_5xx")
        cart_repo_mock.claim_expired_for_processing.return_value = [cart]
        product_service_mock.find_product.return_value = ProductFactory.create()
        store_payment_info_mock.get_complete_by_store.return_value = PaymentInfoFactory.create()
        payment_gateway_mock.fetch_status.side_effect = PortOneTransientError("502")

        result = await service.sweep_expired_carts(limit=100)

        assert result.transient == 1
        assert result.finalized == 0
        assert result.cancelled == 0
        # cart 도 재고도 손대지 않아야 한다.
        order_query_mock.create_order_from_cart.assert_not_awaited()
        product_service_mock.restore_purchased_stock.assert_not_awaited()


    async def test_payment_info_missing_treated_as_transient(
        self,
        service,
        cart_repo_mock,
        product_service_mock,
        store_payment_info_mock,
        payment_gateway_mock,
    ):
        """가게가 결제 설정을 지움 — 검증 불가. cart 손대지 않고 운영자 알람."""
        cart = CartItemFactory.create(payment_id="PAY_noinfo")
        cart_repo_mock.claim_expired_for_processing.return_value = [cart]
        product_service_mock.find_product.return_value = ProductFactory.create()
        store_payment_info_mock.get_complete_by_store.side_effect = PaymentInfoMissingError("gone")

        result = await service.sweep_expired_carts(limit=100)

        assert result.transient == 1
        payment_gateway_mock.fetch_status.assert_not_awaited()


    async def test_restore_stock_failure_keeps_cart_for_next_sweep(
        self,
        service,
        cart_repo_mock,
        product_service_mock,
        store_payment_info_mock,
        payment_gateway_mock,
        order_query_mock,
    ):
        """재고 복구 실패 시 cart 는 살아남아야 한다 — SAVEPOINT 가 delete 와 함께 롤백.

        regression test for: ``_restore_stock_in_tx`` 의 swallow 가 SAVEPOINT 의 atomicity 를
        깨뜨려 재고 손실 + cart 삭제가 같이 일어나던 버그.
        """
        cart = CartItemFactory.create(
            payment_id="PAY_restorefail", product_id="PRD_x", quantity=2,
        )
        cart_repo_mock.claim_expired_for_processing.return_value = [cart]
        product_service_mock.find_product.return_value = ProductFactory.create()
        store_payment_info_mock.get_complete_by_store.return_value = PaymentInfoFactory.create()
        payment_gateway_mock.fetch_status.return_value = None  # not paid → cancel branch

        # 재고 복구가 실패. swallow 가 사라졌으면 SAVEPOINT 에서 예외가 보임 → delete 미실행.
        product_service_mock.restore_purchased_stock.side_effect = RuntimeError(
            "stock conflict exhausted retries",
        )

        result = await service.sweep_expired_carts(limit=100)

        # cart 는 그대로 유지 — 다음 sweep 에서 재시도.
        order_query_mock.delete_cart_item.assert_not_awaited()
        # finalized / cancelled 어디에도 카운트 안 됨 (Exception 분기).
        assert result.finalized == 0
        assert result.cancelled == 0
        assert result.transient == 0


    async def test_mixed_batch_isolated_outcomes(
        self,
        service,
        cart_repo_mock,
        product_service_mock,
        store_payment_info_mock,
        payment_gateway_mock,
    ):
        """SAVEPOINT 격리 — 같은 batch 안에서 다양한 결과가 섞여도 카운팅 정확."""
        paid_cart = CartItemFactory.create(
            payment_id="PAY_paid", customer_id="alice@example.com", total_amount=10000,
        )
        noshow_cart = CartItemFactory.create(payment_id="PAY_noshow")
        transient_cart = CartItemFactory.create(payment_id="PAY_5xx")
        cart_repo_mock.claim_expired_for_processing.return_value = [
            paid_cart, noshow_cart, transient_cart,
        ]
        product_service_mock.find_product.return_value = ProductFactory.create()
        store_payment_info_mock.get_complete_by_store.return_value = PaymentInfoFactory.create()

        # cart 별로 다른 결과 — call 순서대로 반환.
        payment_gateway_mock.fetch_status.side_effect = [
            _paid(10000),                          # PAY_paid → finalized
            None,                                  # PAY_noshow → cancelled
            PortOneTransientError("503"),          # PAY_5xx → transient
        ]

        result = await service.sweep_expired_carts(limit=100)

        assert result.finalized == 1
        assert result.cancelled == 1
        assert result.transient == 1
        assert result.finalized_customer_emails == ["alice@example.com"]
