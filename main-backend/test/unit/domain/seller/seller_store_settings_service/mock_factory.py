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
    session.refresh = AsyncMock()
    return session


class StoreRepoMockFactory:
    @classmethod
    def create(cls) -> AsyncMock:
        mock = AsyncMock()
        mock.get_with_address.return_value = None
        mock.update.return_value = None
        return mock


class StoreAddressRepoMockFactory:
    @classmethod
    def create(cls) -> AsyncMock:
        mock = AsyncMock()
        mock.update.return_value = None
        return mock


class OperationRepoMockFactory:
    @classmethod
    def create(cls) -> AsyncMock:
        mock = AsyncMock()
        mock.get_by_store_id.return_value = []
        mock.get_many.return_value = []
        mock.get_by_day_of_week.return_value = []
        mock.update_today_open_status_for_stores.return_value = 0
        mock.apply_modification.return_value = 1
        return mock


class ModificationRepoMockFactory:
    @classmethod
    def create(cls) -> AsyncMock:
        mock = AsyncMock()
        mock.get_by_store_id.return_value = []
        mock.get_all_with_operation_info.return_value = []
        mock.create_modifications_batch.return_value = []
        mock.update_modifications_batch.return_value = []
        mock.delete_all_by_store_id.return_value = 0
        mock.delete_by_modification_id.return_value = None
        return mock


class InternalPaymentClientMockFactory:
    """payment-backend 호출 mock — settings 서비스가 사용하는 has_complete_info 만."""

    @classmethod
    def create(cls) -> AsyncMock:
        mock = AsyncMock()
        mock.has_complete_info.return_value = True
        return mock
