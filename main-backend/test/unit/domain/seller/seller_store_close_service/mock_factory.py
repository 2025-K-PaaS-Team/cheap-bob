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


class OperationRepoMockFactory:
    @classmethod
    def create(cls) -> AsyncMock:
        mock = AsyncMock()
        mock.get_today_operation_info.return_value = None
        mock.update_open_status.return_value = None
        return mock


class OrderQueryServiceMockFactory:
    @classmethod
    def create(cls) -> AsyncMock:
        mock = AsyncMock()
        mock.list_store_current_orders.return_value = []
        mock.cancel_order.return_value = 1
        return mock


class SellerProductServiceMockFactory:
    @classmethod
    def create(cls) -> AsyncMock:
        mock = AsyncMock()
        mock.restore_purchased_stock.return_value = None
        return mock


class InternalPaymentClientMockFactory:
    """payment-backend 호출 mock — has_complete_info / refund 두 메서드만 본 서비스에서 사용."""

    @classmethod
    def create(cls) -> AsyncMock:
        mock = AsyncMock()
        mock.has_complete_info.return_value = True
        mock.refund.return_value = None
        return mock
