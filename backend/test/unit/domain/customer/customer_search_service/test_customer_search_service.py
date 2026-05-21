"""Tests for ``app.domain.customer.service.customer_search.CustomerSearchService``."""
from types import SimpleNamespace
import pytest

from app.domain.customer.service.exception import StoreNotFoundError


def _store(store_id: str) -> SimpleNamespace:
    return SimpleNamespace(store_id=store_id)


@pytest.mark.unit
class TestListStores:

    async def test_decorates_with_favorite_flag(
        self, service, store_read_mock, favorite_repo_mock,
    ):
        store_read_mock.list_with_products.return_value = (
            [_store("STR_a"), _store("STR_b")],
            True,
        )
        favorite_repo_mock.find_store_ids_by_customer.return_value = {"STR_a"}

        result = await service.list_stores(
            customer_email="alice@example.com", page=0,
        )

        assert result.is_end is True
        ids_fav = {(s.store_id, s.is_favorite) for s in result.stores}
        assert ids_fav == {("STR_a", True), ("STR_b", False)}


    async def test_offset_uses_page_size_4(self, service, store_read_mock):
        store_read_mock.list_with_products.return_value = ([], True)
        await service.list_stores(customer_email="alice@example.com", page=2)
        store_read_mock.list_with_products.assert_awaited_once_with(
            offset=8, limit=4,
        )


@pytest.mark.unit
class TestGetStoreProducts:

    async def test_raises_when_store_missing(self, service, store_read_mock):
        store_read_mock.get_with_full_info.return_value = None
        with pytest.raises(StoreNotFoundError):
            await service.get_store_products("STR_x")


    async def test_returns_products(self, service, store_read_mock):
        store_read_mock.get_with_full_info.return_value = SimpleNamespace(
            store_id="STR_x", store_name="가게",
        )
        store_read_mock.get_store_products_with_nutrition.return_value = [
            SimpleNamespace(
                product_id="PRD_1", store_id="STR_x", product_name="A",
                description="", initial_stock=10, current_stock=10,
                price=1000, sale=None, version=1, nutrition_info=[],
            ),
        ]

        result = await service.get_store_products("STR_x")
        assert result.store_id == "STR_x"
        assert len(result.products) == 1


@pytest.mark.unit
class TestSearchByName:

    async def test_returns_decorated_results_and_keyword(
        self, service, store_read_mock, favorite_repo_mock,
    ):
        store_read_mock.search_by_name.return_value = ([_store("STR_a")], False)
        favorite_repo_mock.find_store_ids_by_customer.return_value = set()

        page, keyword = await service.search_by_name(
            customer_email="alice@example.com", search_name="치킨", page=0,
        )
        assert keyword == "치킨"
        assert page.is_end is False
        assert page.stores[0].store_id == "STR_a"
