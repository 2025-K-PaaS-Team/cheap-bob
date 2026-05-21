from unittest.mock import AsyncMock, MagicMock


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


class _PreferenceRepoMock:
    @classmethod
    def create(cls) -> AsyncMock:
        mock = AsyncMock()
        mock.find_by_customer.return_value = []
        mock.save_bulk.side_effect = lambda email, items: items
        mock.delete.return_value = True
        return mock


class MenuRepoMockFactory(_PreferenceRepoMock):
    pass


class NutritionRepoMockFactory(_PreferenceRepoMock):
    pass


class AllergyRepoMockFactory(_PreferenceRepoMock):
    pass


class ToppingRepoMockFactory(_PreferenceRepoMock):
    pass
