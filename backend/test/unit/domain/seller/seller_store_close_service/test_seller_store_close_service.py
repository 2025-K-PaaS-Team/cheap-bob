"""Tests for ``app.domain.seller.service.seller_store_close.SellerStoreCloseService``."""
from types import SimpleNamespace
import pytest

from app.domain.seller.service.exception import StorePaymentMissingError
from app.domain.payment.service.exception import (
    PaymentInfoIncompleteError,
    PaymentInfoMissingError,
)
from app.domain.order.dto.order import OrderStatus


@pytest.mark.unit
class TestClose:

    async def test_payment_missing_raises(self, service, payment_info_mock):
        payment_info_mock.get_complete_by_store.side_effect = (
            PaymentInfoMissingError("missing")
        )
        with pytest.raises(StorePaymentMissingError):
            await service.close("STR_x")


    async def test_payment_incomplete_raises(self, service, payment_info_mock):
        payment_info_mock.get_complete_by_store.side_effect = (
            PaymentInfoIncompleteError("incomplete")
        )
        with pytest.raises(StorePaymentMissingError):
            await service.close("STR_x")


    async def test_no_active_orders_returns_zero(
        self, service, order_query_mock, operation_repo_mock,
    ):
        # today_operation 도 있어 close 처리됨.
        operation_repo_mock.get_today_operation_info.return_value = SimpleNamespace(
            operation_id=1,
        )
        order_query_mock.list_store_current_orders.return_value = []

        count, message = await service.close("STR_x")
        assert count == 0
        assert "마감" in message
        # 운영 상태도 closed 로 토글됐어야 함.
        operation_repo_mock.update_open_status.assert_awaited_once_with(
            operation_id=1, is_currently_open=False,
        )


    async def test_refunds_only_active_orders(
        self, service, order_query_mock, payment_gateway_mock,
        product_service_mock, operation_repo_mock,
    ):
        operation_repo_mock.get_today_operation_info.return_value = None  # 운영정보 없음 OK
        order_query_mock.list_store_current_orders.return_value = [
            SimpleNamespace(
                payment_id="PAY_a", product_id="PRD_a",
                status=OrderStatus.reservation,
            ),
            SimpleNamespace(
                payment_id="PAY_b", product_id="PRD_b",
                status=OrderStatus.accept,
            ),
            SimpleNamespace(
                payment_id="PAY_c", product_id="PRD_c",
                status=OrderStatus.complete,  # 환불 대상 아님
            ),
        ]
        order_query_mock.cancel_order.return_value = 2  # quantity

        count, _ = await service.close("STR_x")

        # reservation + accept 2건만 환불.
        assert count == 2
        assert payment_gateway_mock.refund.await_count == 2
        # 재고도 2건 복구.
        assert product_service_mock.restore_purchased_stock.await_count == 2


    async def test_swallows_per_order_errors(
        self, service, order_query_mock, payment_gateway_mock,
        operation_repo_mock,
    ):
        operation_repo_mock.get_today_operation_info.return_value = None
        order_query_mock.list_store_current_orders.return_value = [
            SimpleNamespace(
                payment_id="PAY_fail", product_id="PRD_a",
                status=OrderStatus.reservation,
            ),
            SimpleNamespace(
                payment_id="PAY_ok", product_id="PRD_b",
                status=OrderStatus.reservation,
            ),
        ]
        payment_gateway_mock.refund.side_effect = [
            RuntimeError("first fails"), {"refunded": True},
        ]

        count, _ = await service.close("STR_x")
        # 첫 건 실패는 swallow, 두 번째만 카운트.
        assert count == 1
