from unittest.mock import AsyncMock, MagicMock

from app.domain.seller.repository.store_product_info import StockUpdateResult


class FakeUnitOfWork:
    def __init__(self, session):
        self._session = session


    async def __aenter__(self):
        return self._session


    async def __aexit__(self, exc_type, exc, tb):
        return False


def make_mock_session() -> MagicMock:
    session = MagicMock(name="session")
    session.flush = AsyncMock()
    return session


class StoreProductInfoRepoMockFactory:
    @classmethod
    def create(cls) -> AsyncMock:
        mock = AsyncMock()
        mock.get_by_product_id.return_value = None
        mock.get_by_store_id.return_value = []
        mock.get_with_nutrition_info.return_value = None
        mock.adjust_purchased_stock.return_value = StockUpdateResult.SUCCESS
        mock.adjust_admin_stock.return_value = StockUpdateResult.SUCCESS
        mock.set_stock.return_value = StockUpdateResult.SUCCESS
        mock.reset_all_inventories.return_value = 0
        mock.update.return_value = None
        return mock


class ProductNutritionRepoMockFactory:
    @classmethod
    def create(cls) -> AsyncMock:
        mock = AsyncMock()
        mock.add_nutrition_with_validation.return_value = ([], [])
        mock.remove_nutrition_from_product.return_value = True
        return mock


class ProductStockReservationServiceMockFactory:
    @classmethod
    def create(cls) -> AsyncMock:
        mock = AsyncMock()
        mock.get_all.return_value = []
        mock.delete_silently.return_value = True
        return mock
