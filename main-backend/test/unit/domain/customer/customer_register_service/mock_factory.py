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


class _BaseRepoMock:
    @classmethod
    def create(cls) -> AsyncMock:
        mock = AsyncMock()
        mock.save_bulk.return_value = []
        return mock


class DetailRepoMockFactory:
    @classmethod
    def create(cls) -> AsyncMock:
        mock = AsyncMock()
        mock.exists_by_customer.return_value = False
        mock.save.side_effect = lambda detail: detail  # echo passed-in detail
        return mock


class PreferredMenuRepoMockFactory(_BaseRepoMock):
    pass


class NutritionTypeRepoMockFactory(_BaseRepoMock):
    pass


class AllergyRepoMockFactory(_BaseRepoMock):
    pass


class ToppingTypeRepoMockFactory(_BaseRepoMock):
    pass
