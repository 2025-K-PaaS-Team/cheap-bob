"""OrderQueryService + CartItem / OrderCurrentItem 의 실 DB 흐름.

비즈니스 시나리오:
  1) ``create_cart_item`` 으로 임시 장바구니 row 생성
  2) ``get_cart_item`` 으로 조회 가능
  3) ``create_order_from_cart`` 로 정식 주문 (OrderCurrentItem) 생성
  4) ``delete_cart_item`` 으로 cart 정리
  5) ``store_purchased_quantities`` 가 가게의 product 별 누계 반환 (cancel 제외)
  6) ``has_active_orders_for_customer`` 가 reservation/accept 만 카운트
"""
from datetime import datetime, timezone
import pytest
import pytest_asyncio

from app.domain.order.dto.order import OrderStatus
from app.domain.order.repository.order_history_item import OrderHistoryItemRepository
from app.domain.order.service.order_query import OrderQueryService


pytestmark = pytest.mark.integration


@pytest_asyncio.fixture
async def seed_store_with_product(session_factory, seed_seller):
    """seller + store + product 한 세트를 심고 (store_id, product_id) 를 돌려준다.

    OrderCurrentItem 은 ``product_id → store_product_info`` FK 를 요구하므로 사전 seed 필요.
    """
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
    """Mongo 가 없는 환경에서 history 가 필요 없는 테스트만 한정 — history_repo 호출 시 에러.

    본 통합 테스트는 history (Mongo) 를 거치지 않는 경로만 검증한다. PostgreSQL 만 있는 환경
    에서도 동작하도록 의도적으로 좁게 잡았다.
    """
    return OrderQueryService(uow=uow, history_repo=OrderHistoryItemRepository())


class TestCartLifecycle:

    async def test_create_get_delete_cart_item(
        self, order_query_service, seed_customer, seed_store_with_product,
    ):
        [customer_email] = await seed_customer(1)
        store_id, product_id = await seed_store_with_product()

        await order_query_service.create_cart_item(
            payment_id="PAY_it_001",
            product_id=product_id,
            customer_id=customer_email,
            quantity=2,
            price=10000,
            sale=None,
            total_amount=20000,
        )

        # 조회.
        cart = await order_query_service.get_cart_item("PAY_it_001")
        assert cart is not None
        assert cart.quantity == 2
        assert cart.total_amount == 20000

        # 삭제.
        await order_query_service.delete_cart_item("PAY_it_001")
        assert await order_query_service.get_cart_item("PAY_it_001") is None


class TestCreateOrderFromCart:

    async def test_promotes_cart_to_reservation_order(
        self, order_query_service, seed_customer, seed_store_with_product,
        session_factory,
    ):
        [customer_email] = await seed_customer(1)
        store_id, product_id = await seed_store_with_product()

        await order_query_service.create_cart_item(
            payment_id="PAY_it_010",
            product_id=product_id,
            customer_id=customer_email,
            quantity=1,
            price=10000,
            sale=None,
            total_amount=10000,
        )
        cart = await order_query_service.get_cart_item("PAY_it_010")

        await order_query_service.create_order_from_cart(
            cart_item=cart,
            preference_snapshot={
                "preferred_menus": "한식",
                "nutrition_types": None,
                "allergies": None,
                "topping_types": None,
            },
        )

        # 직접 DB 에서 OrderCurrentItem 을 가져와 확인.
        from app.domain.order.model.order_current_item import OrderCurrentItem
        async with session_factory() as session:
            order = await session.get(OrderCurrentItem, "PAY_it_010")
            assert order is not None
            assert order.status == OrderStatus.reservation
            assert order.preferred_menus == "한식"
            assert order.product_id == product_id


class TestStorePurchasedQuantities:

    async def test_aggregates_per_product_excluding_cancel(
        self, order_query_service, seed_customer, seed_store_with_product, session_factory,
    ):
        [customer_email] = await seed_customer(1)
        store_id, product_id = await seed_store_with_product()

        # OrderCurrentItem 을 직접 3건 심는다 (status 별).
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
