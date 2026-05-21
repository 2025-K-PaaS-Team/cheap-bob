from unittest.mock import AsyncMock, MagicMock


class FakeUnitOfWork:
    """`@transactional` 의 ``async with self.uow as session:`` 를 만족."""

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


class CustomerRepositoryMockFactory:
    @classmethod
    def create(cls) -> AsyncMock:
        mock = AsyncMock()
        mock.find_by_email.return_value = None
        mock.delete_by_email.return_value = False
        return mock


class SellerRepositoryMockFactory:
    @classmethod
    def create(cls) -> AsyncMock:
        mock = AsyncMock()
        mock.find_by_email.return_value = None
        mock.delete_by_email.return_value = False
        return mock
