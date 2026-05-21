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


class StorePaymentInfoRepoMockFactory:
    @classmethod
    def create(cls) -> AsyncMock:
        mock = AsyncMock()
        mock.get_by_store_id.return_value = None
        mock.exists_by_store_id.return_value = False
        mock.has_complete_info.return_value = False
        mock.create.return_value = None
        mock.delete.return_value = True
        mock.update_portone_info.return_value = None
        return mock
