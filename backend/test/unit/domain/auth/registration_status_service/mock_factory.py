from unittest.mock import AsyncMock


class FakeUnitOfWork:
    """RegistrationStatusService 는 ``@transactional`` 메서드가 없지만 생성자에서 받는다."""

    def __init__(self, session=None):
        self._session = session


    async def __aenter__(self):
        return self._session


    async def __aexit__(self, exc_type, exc, tb):
        return False


class CustomerStatusServiceMockFactory:
    @classmethod
    def create(cls) -> AsyncMock:
        mock = AsyncMock()
        mock.get_status.return_value = "profile"
        return mock


class SellerStatusServiceMockFactory:
    @classmethod
    def create(cls) -> AsyncMock:
        mock = AsyncMock()
        mock.get_status.return_value = "store"
        return mock
