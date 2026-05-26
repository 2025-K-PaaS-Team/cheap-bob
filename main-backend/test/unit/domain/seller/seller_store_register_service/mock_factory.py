from unittest.mock import AsyncMock, MagicMock
from types import SimpleNamespace


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
    session.refresh = AsyncMock()
    return session


class StoreRepoMockFactory:
    @classmethod
    def create(cls) -> AsyncMock:
        mock = AsyncMock()
        mock.get_by_seller_email.return_value = []
        mock.create.return_value = SimpleNamespace(store_id="STR_fixed")
        return mock


class StoreAddressRepoMockFactory:
    @classmethod
    def create(cls) -> AsyncMock:
        mock = AsyncMock()
        mock.create.return_value = SimpleNamespace(address_id=1)
        return mock


class StoreSNSRepoMockFactory:
    @classmethod
    def create(cls) -> AsyncMock:
        mock = AsyncMock()
        mock.create.return_value = SimpleNamespace(sns_id=1)
        return mock


class StoreOperationRepoMockFactory:
    @classmethod
    def create(cls) -> AsyncMock:
        mock = AsyncMock()
        mock.create_initial_operation_info.return_value = []
        return mock
