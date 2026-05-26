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


class OrderCurrentItemRepoMockFactory:
    @classmethod
    def create(cls) -> AsyncMock:
        mock = AsyncMock()
        mock.get_store_orders_with_relations.return_value = []
        mock.get_store_current_orders_with_relations.return_value = []
        mock.get_order_with_relations.return_value = None
        mock.get_all_orders_with_relations.return_value = []
        mock.update.return_value = None
        mock.cancel_order.return_value = 0
        mock.complete_order.return_value = None
        return mock


class HistoryRepoMockFactory:
    @classmethod
    def create(cls) -> AsyncMock:
        mock = AsyncMock()
        mock.get_store_history.return_value = []
        return mock


class StoreReadServiceMockFactory:
    @classmethod
    def create(cls) -> AsyncMock:
        mock = AsyncMock()
        mock.get_with_full_info.return_value = SimpleNamespace(store_name="가게")
        return mock


class SellerProductServiceMockFactory:
    @classmethod
    def create(cls) -> AsyncMock:
        mock = AsyncMock()
        mock.restore_purchased_stock.return_value = None
        mock.list_by_store.return_value = []
        return mock


class OrderQueryServiceMockFactory:
    @classmethod
    def create(cls) -> AsyncMock:
        mock = AsyncMock()
        mock.store_purchased_quantities.return_value = {}
        mock.list_store_current_orders.return_value = []
        return mock


class InternalPaymentClientMockFactory:
    """payment-svc HTTP 호출 mock — seller_order 가 refund + has_complete_info 사용."""

    @classmethod
    def create(cls) -> AsyncMock:
        mock = AsyncMock()
        mock.refund.return_value = None
        mock.has_complete_info.return_value = True
        return mock


class BackgroundTasksFakeFactory:
    @classmethod
    def create(cls):
        tasks: list = []

        class _FakeBT:
            def add_task(self, fn, *args, **kwargs):
                tasks.append((fn, args, kwargs))

        return _FakeBT(), tasks
