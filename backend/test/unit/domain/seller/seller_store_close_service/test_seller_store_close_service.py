"""Tests for ``app.domain.seller.service.seller_store_close.SellerStoreCloseService``.

payment-svc 분리 후: 환불은 InternalPaymentClient.refund() HTTP 위임, 사전 has_complete_info 체크.
"""
from types import SimpleNamespace
import pytest

from app.domain.seller.service.exception import StorePaymentMissingError
from app.domain.order.dto.order import OrderStatus
from app.core.internal_client.payment import (
    PaymentServiceError,
    PaymentServiceUnavailableError,
)


@pytest.mark.unit
class TestClose:

    async def test_payment_missing_raises(self, service, payment_client_mock):
        payment_client_mock.has_complete_info.return_value = False
        with pytest.raises(StorePaymentMissingError):
            await service.close("STR_x")


    async def test_payment_svc_unavailable_raises(self, service, payment_client_mock):
        payment_client_mock.has_complete_info.side_effect = (
            PaymentServiceUnavailableError(503, "down")
        )
        with pytest.raises(StorePaymentMissingError):
            await service.close("STR_x")


    async def test_no_active_orders_returns_zero(
        self, service, order_query_mock, operation_repo_mock,
    ):
        operation_repo_mock.get_today_operation_info.return_value = SimpleNamespace(
            operation_id=1,
        )
        order_query_mock.list_store_current_orders.return_value = []

        count, message = await service.close("STR_x")
        assert count == 0
        assert "마감" in message
        operation_repo_mock.update_open_status.assert_awaited_once_with(
            operation_id=1, is_currently_open=False,
        )


    async def test_refunds_only_active_orders(
        self, service, order_query_mock, payment_client_mock,
        product_service_mock, operation_repo_mock,
    ):
        operation_repo_mock.get_today_operation_info.return_value = None
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
                status=OrderStatus.complete,
            ),
        ]
        order_query_mock.cancel_order.return_value = 2

        count, _ = await service.close("STR_x")

        assert count == 2
        assert payment_client_mock.refund.await_count == 2
        assert product_service_mock.restore_purchased_stock.await_count == 2


    async def test_swallows_per_order_errors(
        self, service, order_query_mock, payment_client_mock,
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
        payment_client_mock.refund.side_effect = [
            PaymentServiceError(500, "first fails"), None,
        ]

        count, _ = await service.close("STR_x")
        assert count == 1
