"""SellerSettlementService 의 실 DB 흐름.

본 서비스는 ``OrderQueryService`` 위임층이라, 통합 테스트 범위는
"OrderCurrentItem 만 있는 경우" (Mongo history 미사용) 에 한정한다.

비즈니스 시나리오:
  1) ``get_weekly_revenue`` 가 complete 상태 주문의 total_amount 합을 반환 (cancel / reservation 제외)

``weekly_revenue`` 는 월요일이 아닌 날 Mongo history 조회로 분기하므로, history_repo 만
빈 결과를 돌려주는 stub 으로 주입해 외부 의존을 끊는다.
"""
import pytest_asyncio
import pytest
from datetime import datetime, timezone

from app.domain.seller.service.seller_settlement import SellerSettlementService
from app.domain.order.service.order_query import OrderQueryService
from app.domain.order.dto.order import OrderStatus


pytestmark = pytest.mark.integration


class _EmptyHistoryRepo:
    """OrderHistoryItemRepository 의 stub — Mongo 의존 끊기."""

    async def get_store_history(self, **_):
        return []


@pytest_asyncio.fixture
def seller_settlement_service(uow):
    return SellerSettlementService(
        uow=uow,
        order_query_service=OrderQueryService(
            uow=uow, history_repo=_EmptyHistoryRepo(),
        ),
    )


@pytest_asyncio.fixture
async def seed_store_with_product(session_factory, seed_seller):
    from app.domain.seller.model.store import Store
    from app.domain.seller.model.store_product_info import StoreProductInfo

    counter = {"value": 0}

    async def _seed() -> tuple[str, str]:
        [seller_email] = await seed_seller(1)
        async with session_factory() as session:
            idx = counter["value"]
            counter["value"] += 1
            store_id = f"STR_stl_{idx:03d}"
            product_id = f"PRD_stl_{idx:03d}"
            session.add(Store(
                store_id=store_id, store_name="가게", seller_email=seller_email,
            ))
            await session.flush()
            session.add(StoreProductInfo(
                product_id=product_id, store_id=store_id,
                product_name="상품", initial_stock=10, price=10000,
            ))
            await session.commit()
        return store_id, product_id

    return _seed


class TestWeeklyRevenue:

    async def test_sums_complete_orders_only(
        self,
        seller_settlement_service,
        seed_customer,
        seed_store_with_product,
        session_factory,
    ):
        [customer_email] = await seed_customer(1)
        store_id, product_id = await seed_store_with_product()

        from app.domain.order.model.order_current_item import OrderCurrentItem
        now = datetime.now(timezone.utc)
        async with session_factory() as session:
            session.add(OrderCurrentItem(
                payment_id="PAY_stl_1", product_id=product_id, customer_id=customer_email,
                quantity=1, price=10000, total_amount=10000,
                status=OrderStatus.complete, reservation_at=now, completed_at=now,
            ))
            session.add(OrderCurrentItem(
                payment_id="PAY_stl_2", product_id=product_id, customer_id=customer_email,
                quantity=2, price=10000, total_amount=20000,
                status=OrderStatus.complete, reservation_at=now, completed_at=now,
            ))
            session.add(OrderCurrentItem(
                payment_id="PAY_stl_3", product_id=product_id, customer_id=customer_email,
                quantity=5, price=10000, total_amount=50000,
                status=OrderStatus.cancel, reservation_at=now, canceled_at=now,
            ))
            await session.commit()

        revenue = await seller_settlement_service.get_weekly_revenue(store_id)
        assert revenue == 30000
