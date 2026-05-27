"""Tests for ``app.domain.seller.service.seller_store_close.SellerStoreCloseService``.

Phase 5.2 — 환불은 outbox 이벤트로 위임. 본 서비스는 사전 체크 + 운영 상태 변경 + 이벤트 enqueue 만 담당.
실제 PortOne 호출 / OrderCurrentItem cancel / stock restore 는 컨슈머 핸들러 책임이라 본 단위
테스트 범위가 아니다.
"""
from types import SimpleNamespace
import pytest

from app.domain.seller.service.exception import StorePaymentMissingError
from app.domain.order.dto.order import OrderStatus
from app.core.internal_client.payment import PaymentServiceUnavailableError


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
        self, service, order_query_mock, operation_repo_mock, enqueue_event_mock,
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
        enqueue_event_mock.assert_not_awaited()


    async def test_emits_refund_event_only_for_active_orders(
        self, service, order_query_mock, operation_repo_mock, enqueue_event_mock,
    ):
        operation_repo_mock.get_today_operation_info.return_value = None

        def _order(payment_id, product_id, quantity, status):
            # order.product.store.store_name 까지 relation chain 필요 — SimpleNamespace 중첩.
            return SimpleNamespace(
                payment_id=payment_id,
                product_id=product_id,
                quantity=quantity,
                customer_id=f"{payment_id.lower()}@example.com",
                status=status,
                product=SimpleNamespace(
                    store=SimpleNamespace(store_name="테스트 가게"),
                ),
            )

        order_query_mock.list_store_current_orders.return_value = [
            _order("PAY_a", "PRD_a", 2, OrderStatus.reservation),
            _order("PAY_b", "PRD_b", 1, OrderStatus.accept),
            _order("PAY_c", "PRD_c", 3, OrderStatus.complete),
        ]

        count, _ = await service.close("STR_x")

        assert count == 2
        assert enqueue_event_mock.await_count == 2

        topics = [
            call.kwargs["topic"] for call in enqueue_event_mock.await_args_list
        ]
        assert topics == [
            "order.refund.requested", "order.refund.requested",
        ]
        aggregate_ids = [
            call.kwargs["aggregate_id"] for call in enqueue_event_mock.await_args_list
        ]
        assert aggregate_ids == ["PAY_a", "PAY_b"]

        # payload echo 검증 — completed 핸들러가 별도 lookup 없이 cancel + restore + 이메일.
        first_payload = enqueue_event_mock.await_args_list[0].kwargs["payload"]
        assert first_payload == {
            "payment_id": "PAY_a",
            "store_id": "STR_x",
            "store_name": "테스트 가게",
            "customer_id": "pay_a@example.com",
            "product_id": "PRD_a",
            "quantity": 2,
            "reason": "'기타 사정' 으로 주문이 취소되었어요.",
        }
