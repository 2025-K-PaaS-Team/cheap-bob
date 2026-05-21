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
    session.delete = AsyncMock()
    return session


class WithdrawRepoMockFactory:
    @classmethod
    def create(cls) -> AsyncMock:
        mock = AsyncMock()
        mock.save.return_value = None
        mock.find_by_seller_email.return_value = None
        mock.delete_by_seller_email.return_value = None
        mock.get_many.return_value = []
        mock.delete_by_id.return_value = None
        return mock


class AuthAccountServiceMockFactory:
    @classmethod
    def create(cls) -> AsyncMock:
        mock = AsyncMock()
        mock.is_seller_active.return_value = True
        mock.set_seller_active.return_value = None
        mock.hard_delete_seller.return_value = True
        return mock


class PaymentInfoServiceMockFactory:
    @classmethod
    def create(cls) -> AsyncMock:
        mock = AsyncMock()
        mock.delete_by_store.return_value = True
        return mock


class StoreRepoMockFactory:
    @classmethod
    def create(cls) -> AsyncMock:
        mock = AsyncMock()
        mock.get_by_seller_email.return_value = []
        mock.delete.return_value = True
        return mock


class ProductRepoMockFactory:
    @classmethod
    def create(cls) -> AsyncMock:
        mock = AsyncMock()
        mock.get_by_store_id.return_value = []
        mock.delete.return_value = True
        return mock


class OperationRepoMockFactory:
    @classmethod
    def create(cls) -> AsyncMock:
        mock = AsyncMock()
        mock.get_by_store_and_day.return_value = None
        mock.get_many.return_value = []
        return mock


class ImageRepoMockFactory:
    @classmethod
    def create(cls) -> AsyncMock:
        mock = AsyncMock()
        mock.get_by_store_id.return_value = []
        return mock


class SnsRepoMockFactory:
    @classmethod
    def create(cls) -> AsyncMock:
        mock = AsyncMock()
        mock.get_by_store_id.return_value = None
        return mock
