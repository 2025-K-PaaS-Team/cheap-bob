from unittest.mock import AsyncMock


class FakeUnitOfWork:
    def __init__(self, session=None):
        self._session = session


    async def __aenter__(self):
        return self._session


    async def __aexit__(self, exc_type, exc, tb):
        return False


class WithdrawRepoMockFactory:
    @classmethod
    def create(cls) -> AsyncMock:
        mock = AsyncMock()
        mock.save.return_value = None
        mock.get_many.return_value = []
        mock.find_by_customer_email.return_value = None
        mock.delete_by_customer_email.return_value = None
        mock.delete_by_id.return_value = None
        return mock


class OrderQueryServiceMockFactory:
    @classmethod
    def create(cls) -> AsyncMock:
        mock = AsyncMock()
        mock.has_active_orders_for_customer.return_value = False
        return mock


class AuthAccountServiceMockFactory:
    @classmethod
    def create(cls) -> AsyncMock:
        mock = AsyncMock()
        mock.is_customer_active.return_value = True
        mock.set_customer_active.return_value = None
        mock.hard_delete_customer.return_value = True
        return mock
