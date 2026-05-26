"""OrderQueryService + OrderCurrentItem 의 실 DB 흐름.

비즈니스 시나리오:
  1) ``store_purchased_quantities`` 가 가게의 product 별 누계 반환 (cancel 제외)
  2) ``has_active_orders_for_customer`` 가 reservation/accept 만 카운트

cart_item / create_order_from_cart 흐름은 MSA 분리되어 backend-payment 가 소유 +
backend 의 /api/internal/order/orders/from-cart 엔드포인트로 노출. 본 모듈에서는 다루지 않음.
"""
import pytest_asyncio
import pytest
from datetime import datetime, timezone

from app.domain.order.service.order_query import OrderQueryService
from app.domain.order.repository.order_history_item import OrderHistoryItemRepository
from app.domain.order.dto.order import OrderStatus


pytestmark = pytest.mark.integration


@pytest_asyncio.fixture
async def seed_store_with_product(session_factory, seed_seller):
    """seller + store + product 한 세트를 심고 (store_id, product_id) 를 돌려준다."""
    from app.domain.seller.model.store import Store
    from app.domain.seller.model.store_product_info import StoreProductInfo

    counter = {"value": 0}

    async def _seed():
        [seller_email] = await seed_seller(1)
        async with session_factory() as session:
            idx = counter["value"]
            counter["value"] += 1
            store_id = f"STR_it_{idx:03d}"
            product_id = f"PRD_it_{idx:03d}"
            session.add(Store(
                store_id=store_id,
                store_name=f"가게_{idx}",
                seller_email=seller_email,
            ))
            await session.flush()
            session.add(StoreProductInfo(
                product_id=product_id,
                store_id=store_id,
                product_name=f"상품_{idx}",
                initial_stock=10,
                price=10000,
            ))
            await session.commit()
        return store_id, product_id

    return _seed


@pytest_asyncio.fixture
def order_query_service(uow):
    """Mongo 가 없는 환경에서 history 가 필요 없는 테스트만 한정."""
    return OrderQueryService(uow=uow, history_repo=OrderHistoryItemRepository())


class TestStorePurchasedQuantities:

    async def test_aggregates_per_product_excluding_cancel(
        self, order_query_service, seed_customer, seed_store_with_product, session_factory,
    ):
        [customer_email] = await seed_customer(1)
        store_id, product_id = await seed_store_with_product()

        from app.domain.order.model.order_current_item import OrderCurrentItem
        now = datetime.now(timezone.utc)
        async with session_factory() as session:
            session.add(OrderCurrentItem(
                payment_id="PAY_a", product_id=product_id, customer_id=customer_email,
                quantity=2, price=10000, total_amount=20000,
                status=OrderStatus.reservation, reservation_at=now,
            ))
            session.add(OrderCurrentItem(
                payment_id="PAY_b", product_id=product_id, customer_id=customer_email,
                quantity=3, price=10000, total_amount=30000,
                status=OrderStatus.complete, reservation_at=now, completed_at=now,
            ))
            session.add(OrderCurrentItem(
                payment_id="PAY_c", product_id=product_id, customer_id=customer_email,
                quantity=5, price=10000, total_amount=50000,
                status=OrderStatus.cancel, reservation_at=now, canceled_at=now,
            ))
            await session.commit()

        totals = await order_query_service.store_purchased_quantities(store_id)
        # cancel 은 제외 → 2 + 3 = 5
        assert totals.get(product_id) == 5


class TestActiveOrderDetection:

    async def test_returns_true_when_reservation_exists(
        self, order_query_service, seed_customer, seed_store_with_product, session_factory,
    ):
        [customer_email] = await seed_customer(1)
        _, product_id = await seed_store_with_product()

        from app.domain.order.model.order_current_item import OrderCurrentItem
        now = datetime.now(timezone.utc)
        async with session_factory() as session:
            session.add(OrderCurrentItem(
                payment_id="PAY_r", product_id=product_id, customer_id=customer_email,
                quantity=1, price=10000, total_amount=10000,
                status=OrderStatus.reservation, reservation_at=now,
            ))
            await session.commit()

        assert await order_query_service.has_active_orders_for_customer(customer_email) is True


    async def test_returns_false_when_only_completed_or_cancelled(
        self, order_query_service, seed_customer, seed_store_with_product, session_factory,
    ):
        [customer_email] = await seed_customer(1)
        _, product_id = await seed_store_with_product()

        from app.domain.order.model.order_current_item import OrderCurrentItem
        now = datetime.now(timezone.utc)
        async with session_factory() as session:
            session.add(OrderCurrentItem(
                payment_id="PAY_c1", product_id=product_id, customer_id=customer_email,
                quantity=1, price=10000, total_amount=10000,
                status=OrderStatus.complete, reservation_at=now, completed_at=now,
            ))
            session.add(OrderCurrentItem(
                payment_id="PAY_c2", product_id=product_id, customer_id=customer_email,
                quantity=1, price=10000, total_amount=10000,
                status=OrderStatus.cancel, reservation_at=now, canceled_at=now,
            ))
            await session.commit()

        assert await order_query_service.has_active_orders_for_customer(customer_email) is False
