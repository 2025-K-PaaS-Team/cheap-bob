from unittest.mock import AsyncMock, MagicMock


class FakeUnitOfWork:
    def __init__(self, session):
        self._session = session


    async def __aenter__(self):
        return self._session


    async def __aexit__(self, exc_type, exc, tb):
        return False


def make_mock_session() -> MagicMock:
    return MagicMock(name="session")


class FavoriteRepoMockFactory:
    @classmethod
    def create(cls) -> AsyncMock:
        mock = AsyncMock()
        mock.find_store_ids_by_customer.return_value = set()
        return mock


class StoreReadServiceMockFactory:
    @classmethod
    def create(cls) -> AsyncMock:
        mock = AsyncMock()
        mock.list_with_products.return_value = ([], True)
        mock.search_by_location.return_value = ([], True)
        mock.search_by_name.return_value = ([], True)
        mock.search_by_location_and_name.return_value = ([], True)
        mock.get_with_full_info.return_value = None
        mock.get_store_products_with_nutrition.return_value = []
        mock.get_favorite_stores_by_customer.return_value = []
        return mock


class HistoryServiceMockFactory:
    @classmethod
    def create(cls) -> AsyncMock:
        return AsyncMock()
