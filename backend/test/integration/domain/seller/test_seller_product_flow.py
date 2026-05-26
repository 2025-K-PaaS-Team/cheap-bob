"""SellerProductService 의 실 DB 흐름 (재고 예약 Mongo 경로 제외).

비즈니스 시나리오:
  1) ``create`` 가 product + nutrition 한 트랜잭션으로 등록 (MVP 1가게=1상품 제약)
  2) ``get`` 은 store_id ownership 까지 확인 — 다른 가게 product 조회는 미발견 처리
  3) ``update`` 는 부분 패치 + sale=0 → None 변환
  4) ``consume_purchased_stock`` / ``restore_purchased_stock`` 이 purchased_quantity 를 +/- 조정
  5) ``adjust_admin_stock`` 은 admin_adjustment 누적, 재고 부족 시 ``ProductStockInsufficientError``
  6) ``add_nutrition`` 중복 시 ``ProductNutritionDuplicateError``, 정상 시 합본 반환
  7) ``remove_nutrition`` 누락 시 ``ProductNutritionNotFoundError``

``SellerProductService`` 가 생성자에서 받는 ``product_stock_reservation_service`` 는 Mongo 의존이라
본 통합 테스트에서는 ``None`` 으로 주입한다 — 재고 예약 경로 메서드는 호출하지 않으므로 안전.
"""
import pytest_asyncio
import pytest

from app.domain.seller.service.seller_product import SellerProductService
from app.domain.seller.service.exception import (
    ProductAlreadyRegisteredError,
    ProductNotFoundError,
    ProductNutritionDuplicateError,
    ProductNutritionNotFoundError,
    ProductStockInsufficientError,
)
from app.domain.seller.dto.nutrition import NutritionType


pytestmark = pytest.mark.integration


@pytest_asyncio.fixture
def seller_product_service(uow):
    # Mongo 기반 stock_reservation_service 는 본 테스트에서 미사용 → None.
    return SellerProductService(uow=uow, product_stock_reservation_service=None)


@pytest_asyncio.fixture
async def seed_store(session_factory, seed_seller):
    from app.domain.seller.model.store import Store

    counter = {"value": 0}

    async def _seed() -> str:
        [seller_email] = await seed_seller(1)
        async with session_factory() as session:
            idx = counter["value"]
            counter["value"] += 1
            store_id = f"STR_prod_{idx:03d}"
            session.add(Store(
                store_id=store_id, store_name="가게", seller_email=seller_email,
            ))
            await session.commit()
        return store_id

    return _seed


class TestCreate:

    async def test_persists_product_and_nutrition(
        self, seller_product_service, seed_store, session_factory,
    ):
        store_id = await seed_store()

        product, nutritions = await seller_product_service.create(
            store_id=store_id,
            product_name="단백질샐러드",
            description="고단백",
            initial_stock=20,
            price=12000,
            sale=10,
            nutrition_types=[NutritionType.protein, NutritionType.diet],
        )
        assert product.product_name == "단백질샐러드"
        assert set(nutritions) == {NutritionType.protein, NutritionType.diet}

        from app.domain.seller.model.product_nutrition import ProductNutrition
        from sqlalchemy import select
        async with session_factory() as session:
            result = await session.execute(
                select(ProductNutrition).where(
                    ProductNutrition.product_id == product.product_id,
                ),
            )
            assert len(result.scalars().all()) == 2


    async def test_second_create_raises(self, seller_product_service, seed_store):
        store_id = await seed_store()
        await seller_product_service.create(
            store_id=store_id,
            product_name="A", description="", initial_stock=1, price=1000,
            sale=None, nutrition_types=[],
        )
        with pytest.raises(ProductAlreadyRegisteredError):
            await seller_product_service.create(
                store_id=store_id,
                product_name="B", description="", initial_stock=1, price=1000,
                sale=None, nutrition_types=[],
            )


class TestGetAndUpdate:

    async def test_get_returns_with_nutrition_only_for_owner(
        self, seller_product_service, seed_store,
    ):
        store_id = await seed_store()
        other_store = await seed_store()
        created, _ = await seller_product_service.create(
            store_id=store_id,
            product_name="P", description="", initial_stock=1, price=1000,
            sale=None, nutrition_types=[NutritionType.protein],
        )

        product, nutritions = await seller_product_service.get(
            store_id=store_id, product_id=created.product_id,
        )
        assert product.product_id == created.product_id
        assert nutritions == [NutritionType.protein]

        with pytest.raises(ProductNotFoundError):
            await seller_product_service.get(
                store_id=other_store, product_id=created.product_id,
            )


    async def test_update_partial_and_sale_zero_clears(
        self, seller_product_service, seed_store,
    ):
        store_id = await seed_store()
        product, _ = await seller_product_service.create(
            store_id=store_id,
            product_name="원본", description="", initial_stock=1, price=10000,
            sale=20, nutrition_types=[],
        )

        updated, _ = await seller_product_service.update(
            store_id=store_id,
            product_id=product.product_id,
            update_data={"product_name": "수정", "sale": 0},
        )
        assert updated.product_name == "수정"
        assert updated.sale is None


class TestStockAdjust:

    async def test_consume_and_restore_purchased(
        self, seller_product_service, seed_store, session_factory,
    ):
        store_id = await seed_store()
        product, _ = await seller_product_service.create(
            store_id=store_id,
            product_name="P", description="", initial_stock=10, price=1000,
            sale=None, nutrition_types=[],
        )

        await seller_product_service.consume_purchased_stock(
            product_id=product.product_id, quantity=3,
        )

        from app.domain.seller.model.store_product_info import StoreProductInfo
        async with session_factory() as session:
            p = await session.get(StoreProductInfo, product.product_id)
            assert p.purchased_quantity == 3

        await seller_product_service.restore_purchased_stock(
            product_id=product.product_id, quantity=2,
        )
        async with session_factory() as session:
            p = await session.get(StoreProductInfo, product.product_id)
            assert p.purchased_quantity == 1


    async def test_consume_overshoots_current_stock_raises(
        self, seller_product_service, seed_store,
    ):
        store_id = await seed_store()
        product, _ = await seller_product_service.create(
            store_id=store_id,
            product_name="P", description="", initial_stock=5, price=1000,
            sale=None, nutrition_types=[],
        )
        with pytest.raises(ProductStockInsufficientError):
            await seller_product_service.consume_purchased_stock(
                product_id=product.product_id, quantity=10,
            )


    async def test_restore_overshoots_purchased_raises(
        self, seller_product_service, seed_store, session_factory,
    ):
        """누계 차감 (purchased_quantity) 보다 많이 복원하려는 시도는 거부."""
        store_id = await seed_store()
        product, _ = await seller_product_service.create(
            store_id=store_id,
            product_name="P", description="", initial_stock=5, price=1000,
            sale=None, nutrition_types=[],
        )
        await seller_product_service.consume_purchased_stock(
            product_id=product.product_id, quantity=2,
        )
        with pytest.raises(ProductStockInsufficientError):
            await seller_product_service.restore_purchased_stock(
                product_id=product.product_id, quantity=3,
            )
        # purchased_quantity 는 첫 consume 분만 남아야 한다.
        from app.domain.seller.model.store_product_info import StoreProductInfo
        async with session_factory() as session:
            p = await session.get(StoreProductInfo, product.product_id)
            assert p.purchased_quantity == 2


    async def test_admin_adjust_negative_below_zero_raises(
        self, seller_product_service, seed_store,
    ):
        store_id = await seed_store()
        product, _ = await seller_product_service.create(
            store_id=store_id,
            product_name="P", description="", initial_stock=1, price=1000,
            sale=None, nutrition_types=[],
        )

        with pytest.raises(ProductStockInsufficientError):
            await seller_product_service.adjust_admin_stock(
                store_id=store_id, product_id=product.product_id, delta=-2,
            )


    async def test_admin_adjust_increments(
        self, seller_product_service, seed_store, session_factory,
    ):
        store_id = await seed_store()
        product, _ = await seller_product_service.create(
            store_id=store_id,
            product_name="P", description="", initial_stock=5, price=1000,
            sale=None, nutrition_types=[],
        )

        await seller_product_service.adjust_admin_stock(
            store_id=store_id, product_id=product.product_id, delta=3,
        )

        from app.domain.seller.model.store_product_info import StoreProductInfo
        async with session_factory() as session:
            p = await session.get(StoreProductInfo, product.product_id)
            assert p.admin_adjustment == 3
            assert p.current_stock == 8


class TestNutrition:

    async def test_add_duplicate_raises(
        self, seller_product_service, seed_store,
    ):
        store_id = await seed_store()
        product, _ = await seller_product_service.create(
            store_id=store_id,
            product_name="P", description="", initial_stock=1, price=1000,
            sale=None, nutrition_types=[NutritionType.protein],
        )

        with pytest.raises(ProductNutritionDuplicateError):
            await seller_product_service.add_nutrition(
                store_id=store_id,
                product_id=product.product_id,
                nutrition_types=[NutritionType.protein],
            )


    async def test_remove_missing_raises(
        self, seller_product_service, seed_store,
    ):
        store_id = await seed_store()
        product, _ = await seller_product_service.create(
            store_id=store_id,
            product_name="P", description="", initial_stock=1, price=1000,
            sale=None, nutrition_types=[NutritionType.protein],
        )

        with pytest.raises(ProductNutritionNotFoundError):
            await seller_product_service.remove_nutrition(
                store_id=store_id,
                product_id=product.product_id,
                nutrition_types=[NutritionType.diet],
            )


    async def test_remove_existing(
        self, seller_product_service, seed_store, session_factory,
    ):
        store_id = await seed_store()
        product, _ = await seller_product_service.create(
            store_id=store_id,
            product_name="P", description="", initial_stock=1, price=1000,
            sale=None, nutrition_types=[NutritionType.protein, NutritionType.diet],
        )

        _, nutritions = await seller_product_service.remove_nutrition(
            store_id=store_id,
            product_id=product.product_id,
            nutrition_types=[NutritionType.diet],
        )
        assert nutritions == [NutritionType.protein]


class TestResetAllInventories:

    async def test_resets_purchased_and_admin_to_zero(
        self, seller_product_service, seed_store, session_factory,
    ):
        store_id = await seed_store()
        product, _ = await seller_product_service.create(
            store_id=store_id,
            product_name="P", description="", initial_stock=10, price=1000,
            sale=None, nutrition_types=[],
        )
        await seller_product_service.consume_purchased_stock(
            product_id=product.product_id, quantity=2,
        )
        await seller_product_service.adjust_admin_stock(
            store_id=store_id, product_id=product.product_id, delta=1,
        )

        count = await seller_product_service.reset_all_inventories()
        assert count >= 1

        from app.domain.seller.model.store_product_info import StoreProductInfo
        async with session_factory() as session:
            p = await session.get(StoreProductInfo, product.product_id)
            assert p.purchased_quantity == 0
            assert p.admin_adjustment == 0
