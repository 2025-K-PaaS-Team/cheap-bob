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


class StoreRepoMockFactory:
    @classmethod
    def create(cls) -> AsyncMock:
        mock = AsyncMock()
        mock.get_by_seller_email.return_value = []
        mock.create_store_with_full_info.return_value = object()
        return mock
