"""Tests for ``app.domain.seller.service.seller_product.SellerProductService``."""
from types import SimpleNamespace
import pytest

from app.domain.seller.service.exception import (
    ProductAlreadyRegisteredError,
    ProductNotFoundError,
    ProductNutritionDuplicateError,
    ProductNutritionNotFoundError,
    ProductStockConflictError,
    ProductStockInsufficientError,
)
from app.domain.seller.repository.store_product_info import StockUpdateResult
from app.domain.seller.dto.nutrition import NutritionType


def _make_product(**kwargs) -> SimpleNamespace:
    base = dict(
        product_id="PRD_x", store_id="STR_x",
        product_name="P", description="",
        initial_stock=10, purchased_quantity=0, admin_adjustment=0,
        price=10000, sale=None, version=1, current_stock=10,
        nutrition_info=[],
    )
    base.update(kwargs)
    return SimpleNamespace(**base)


@pytest.mark.unit
class TestCreate:

    async def test_raises_when_store_already_has_product(
        self, service, product_repo_mock,
    ):
        product_repo_mock.get_by_store_id.return_value = [SimpleNamespace()]
        with pytest.raises(ProductAlreadyRegisteredError):
            await service.create(
                store_id="STR_x", product_name="A", description="",
                initial_stock=1, price=1000, sale=None, nutrition_types=[],
            )


    async def test_delegates_to_repo_with_generated_id(
        self, service, product_repo_mock, nutrition_repo_mock,
    ):
        product_repo_mock.get_by_store_id.return_value = []
        product_repo_mock.create.return_value = _make_product(product_id="PRD_fixed")

        product, nutritions = await service.create(
            store_id="STR_x", product_name="A", description="",
            initial_stock=1, price=1000, sale=None,
            nutrition_types=[NutritionType.protein],
        )
        assert product.product_id == "PRD_fixed"
        assert nutritions == [NutritionType.protein]
        product_repo_mock.create.assert_awaited_once()
        # generate_product_id 가 주입한 고정값 + nutrition 1건이 별도 INSERT 됐는지.
        assert product_repo_mock.create.await_args.kwargs["product_id"] == "PRD_fixed"
        nutrition_repo_mock.create.assert_awaited_once_with(
            product_id="PRD_fixed", nutrition_type=NutritionType.protein,
        )


@pytest.mark.unit
class TestGet:

    async def test_raises_when_missing(self, service, product_repo_mock):
        product_repo_mock.get_with_nutrition_info.return_value = None
        with pytest.raises(ProductNotFoundError):
            await service.get(store_id="STR_x", product_id="PRD_x")


    async def test_raises_when_other_store(self, service, product_repo_mock):
        product_repo_mock.get_with_nutrition_info.return_value = _make_product(
            store_id="STR_other",
        )
        with pytest.raises(ProductNotFoundError):
            await service.get(store_id="STR_x", product_id="PRD_x")


    async def test_returns_with_nutrition(self, service, product_repo_mock):
        product_repo_mock.get_with_nutrition_info.return_value = _make_product(
            nutrition_info=[
                SimpleNamespace(nutrition_type=NutritionType.diet),
            ],
        )
        _, nutritions = await service.get(store_id="STR_x", product_id="PRD_x")
        assert nutritions == [NutritionType.diet]


@pytest.mark.unit
class TestUpdate:

    async def test_sale_zero_converts_to_none(self, service, product_repo_mock):
        product_repo_mock.get_by_product_id.return_value = _make_product()
        product_repo_mock.get_with_nutrition_info.return_value = _make_product()

        await service.update(
            store_id="STR_x", product_id="PRD_x",
            update_data={"sale": 0},
        )
        # 호출된 update 의 sale 인자가 None 으로 변환됐는지 확인.
        product_repo_mock.update.assert_awaited_once_with("PRD_x", sale=None)


    async def test_raises_when_other_store(self, service, product_repo_mock):
        product_repo_mock.get_by_product_id.return_value = _make_product(
            store_id="STR_other",
        )
        with pytest.raises(ProductNotFoundError):
            await service.update(
                store_id="STR_x", product_id="PRD_x", update_data={},
            )


@pytest.mark.unit
class TestStockAdjust:
    """``_adjust_purchased`` 의 재시도 + 결과 분기."""

    async def test_consume_success(self, service, product_repo_mock):
        product_repo_mock.adjust_purchased_stock.return_value = StockUpdateResult.SUCCESS
        await service.consume_purchased_stock(product_id="PRD_x", quantity=2)
        product_repo_mock.adjust_purchased_stock.assert_awaited_once_with("PRD_x", 2)


    async def test_insufficient_raises_immediately(
        self, service, product_repo_mock,
    ):
        product_repo_mock.adjust_purchased_stock.return_value = (
            StockUpdateResult.INSUFFICIENT_STOCK
        )
        with pytest.raises(ProductStockInsufficientError):
            await service.consume_purchased_stock(product_id="PRD_x", quantity=2)


    async def test_lock_conflict_retries_then_raises(
        self, service, product_repo_mock,
    ):
        product_repo_mock.adjust_purchased_stock.return_value = (
            StockUpdateResult.LOCK_CONFLICT
        )
        with pytest.raises(ProductStockConflictError):
            await service.consume_purchased_stock(product_id="PRD_x", quantity=2)

        # MAX_RETRY_LOCK 만큼 시도해야 한다 (settings.MAX_RETRY_LOCK=3, 환경에 의존).
        assert product_repo_mock.adjust_purchased_stock.await_count >= 2


@pytest.mark.unit
class TestAdminStockAdjust:

    async def test_other_store_raises(self, service, product_repo_mock):
        product_repo_mock.get_by_product_id.return_value = _make_product(
            store_id="STR_other",
        )
        with pytest.raises(ProductNotFoundError):
            await service.adjust_admin_stock(
                store_id="STR_x", product_id="PRD_x", delta=1,
            )


    async def test_insufficient_raises(self, service, product_repo_mock):
        product_repo_mock.get_by_product_id.return_value = _make_product()
        product_repo_mock.adjust_admin_stock.return_value = (
            StockUpdateResult.INSUFFICIENT_STOCK
        )
        with pytest.raises(ProductStockInsufficientError):
            await service.adjust_admin_stock(
                store_id="STR_x", product_id="PRD_x", delta=-100,
            )


    async def test_success_returns_updated_with_nutrition(
        self, service, product_repo_mock,
    ):
        product_repo_mock.get_by_product_id.return_value = _make_product()
        product_repo_mock.adjust_admin_stock.return_value = StockUpdateResult.SUCCESS
        product_repo_mock.get_with_nutrition_info.return_value = _make_product(
            admin_adjustment=1,
            nutrition_info=[
                SimpleNamespace(nutrition_type=NutritionType.protein),
            ],
        )

        product, nutritions = await service.adjust_admin_stock(
            store_id="STR_x", product_id="PRD_x", delta=1,
        )
        assert nutritions == [NutritionType.protein]


@pytest.mark.unit
class TestNutrition:

    async def test_add_duplicate_raises(
        self, service, product_repo_mock, nutrition_repo_mock,
    ):
        product_repo_mock.get_by_product_id.return_value = _make_product()
        nutrition_repo_mock.add_nutrition_with_validation.return_value = (
            [], [NutritionType.protein],
        )
        with pytest.raises(ProductNutritionDuplicateError):
            await service.add_nutrition(
                store_id="STR_x", product_id="PRD_x",
                nutrition_types=[NutritionType.protein],
            )


    async def test_remove_missing_raises(
        self, service, product_repo_mock, nutrition_repo_mock,
    ):
        product_repo_mock.get_by_product_id.return_value = _make_product()
        nutrition_repo_mock.remove_nutrition_from_product.return_value = False
        with pytest.raises(ProductNutritionNotFoundError):
            await service.remove_nutrition(
                store_id="STR_x", product_id="PRD_x",
                nutrition_types=[NutritionType.diet],
            )


@pytest.mark.unit
class TestApplyPendingStockUpdates:

    async def test_returns_zero_when_no_reservations(
        self, service, stock_reservation_mock,
    ):
        stock_reservation_mock.get_all.return_value = []
        assert await service.apply_pending_stock_updates() == (0, 0)


    async def test_skips_when_product_missing(
        self, service, stock_reservation_mock, product_repo_mock,
    ):
        stock_reservation_mock.get_all.return_value = [
            SimpleNamespace(product_id="PRD_missing", initial_stock=10, new_stock=5),
        ]
        product_repo_mock.get_by_product_id.return_value = None

        success, failed = await service.apply_pending_stock_updates()
        # 상품 부재 — success/failed 카운터에 잡히지 않고 silently delete.
        assert success == 0
        assert failed == 0
        stock_reservation_mock.delete_silently.assert_awaited_once_with("PRD_missing")


    async def test_success_increments_counter_and_deletes_reservation(
        self, service, stock_reservation_mock, product_repo_mock,
    ):
        stock_reservation_mock.get_all.return_value = [
            SimpleNamespace(product_id="PRD_x", initial_stock=10, new_stock=20),
        ]
        product_repo_mock.get_by_product_id.return_value = _make_product()
        product_repo_mock.set_stock.return_value = StockUpdateResult.SUCCESS

        success, failed = await service.apply_pending_stock_updates()
        assert success == 1
        assert failed == 0
        stock_reservation_mock.delete_silently.assert_awaited_once_with("PRD_x")
