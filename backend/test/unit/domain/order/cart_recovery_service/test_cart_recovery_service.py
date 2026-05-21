"""Tests for ``app.domain.order.service.cart_recovery.CartRecoveryService``."""
from types import SimpleNamespace
import pytest

from app.domain.seller.service.exception import ProductStockConflictError


def _cart(*, payment_id: str, product_id: str, quantity: int) -> SimpleNamespace:
    return SimpleNamespace(
        payment_id=payment_id, product_id=product_id, quantity=quantity,
    )


@pytest.mark.unit
class TestRecoverAbandonedCarts:

    async def test_returns_zero_when_no_carts(self, service, cart_item_repo_mock):
        cart_item_repo_mock.get_many.return_value = []
        assert await service.recover_abandoned_carts() == 0


    async def test_restores_each_and_deletes(
        self, service, cart_item_repo_mock, product_service_mock, order_query_mock,
    ):
        cart_item_repo_mock.get_many.return_value = [
            _cart(payment_id="PAY_a", product_id="PRD_a", quantity=2),
            _cart(payment_id="PAY_b", product_id="PRD_b", quantity=1),
        ]

        recovered = await service.recover_abandoned_carts()

        assert recovered == 2
        assert product_service_mock.restore_purchased_stock.await_count == 2
        assert order_query_mock.delete_cart_item.await_count == 2


    async def test_swallows_stock_conflict_and_skips_delete(
        self, service, cart_item_repo_mock, product_service_mock, order_query_mock,
    ):
        cart_item_repo_mock.get_many.return_value = [
            _cart(payment_id="PAY_x", product_id="PRD_x", quantity=1),
            _cart(payment_id="PAY_y", product_id="PRD_y", quantity=1),
        ]
        product_service_mock.restore_purchased_stock.side_effect = [
            ProductStockConflictError("lock"), None,
        ]

        recovered = await service.recover_abandoned_carts()

        # 첫 건 stock conflict → continue (delete 안 함). 두 번째만 카운트.
        assert recovered == 1
        assert order_query_mock.delete_cart_item.await_count == 1
        order_query_mock.delete_cart_item.assert_awaited_with("PAY_y")
