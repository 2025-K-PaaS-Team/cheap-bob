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


class OrderCurrentItemRepoMockFactory:
    @classmethod
    def create(cls) -> AsyncMock:
        mock = AsyncMock()
        mock.get_customer_current_orders.return_value = []
        mock.get_customer_current_orders_with_pickup_time.return_value = []
        mock.get_today_alarm_orders.return_value = []
        mock.get_order_with_relations.return_value = None
        mock.complete_order.return_value = None
        mock.cancel_order.return_value = 0
        return mock


class HistoryRepoMockFactory:
    @classmethod
    def create(cls) -> AsyncMock:
        mock = AsyncMock()
        mock.get_customer_history.return_value = []
        mock.get_store_history.return_value = []
        return mock


class SellerStoreReadServiceMockFactory:
    @classmethod
    def create(cls) -> AsyncMock:
        mock = AsyncMock()
        mock.get_with_full_info.return_value = None
        mock.get_today_operation.return_value = None
        return mock


class SellerStoreImageServiceMockFactory:
    @classmethod
    def create(cls) -> AsyncMock:
        mock = AsyncMock()
        mock.get_main_image_urls.return_value = {}
        return mock


class SellerProductServiceMockFactory:
    @classmethod
    def create(cls) -> AsyncMock:
        mock = AsyncMock()
        mock.restore_purchased_stock.return_value = None
        return mock


class PaymentGatewayServiceMockFactory:
    @classmethod
    def create(cls) -> AsyncMock:
        mock = AsyncMock()
        mock.refund.return_value = {"refunded": True}
        return mock


class StorePaymentInfoServiceMockFactory:
    @classmethod
    def create(cls) -> AsyncMock:
        from types import SimpleNamespace
        mock = AsyncMock()
        mock.get_complete_by_store.return_value = SimpleNamespace(
            portone_secret_key="secret-stub",
        )
        return mock


class BackgroundTasksFakeFactory:
    """fastapi.BackgroundTasks 호환 — ``add_task(fn, *a, **kw)`` 만 받아 보관한다."""

    @classmethod
    def create(cls):
        tasks: list = []

        class _FakeBT:
            def add_task(self, fn, *args, **kwargs):
                tasks.append((fn, args, kwargs))

        bt = _FakeBT()
        return bt, tasks
