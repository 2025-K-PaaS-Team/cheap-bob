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


class SellerStoreReadServiceMockFactory:
    @classmethod
    def create(cls) -> AsyncMock:
        mock = AsyncMock()
        mock.get_today_operation.return_value = None
        return mock


class SellerProductServiceMockFactory:
    @classmethod
    def create(cls) -> AsyncMock:
        mock = AsyncMock()
        mock.find_product.return_value = None
        mock.consume_purchased_stock.return_value = None
        mock.restore_purchased_stock.return_value = None
        return mock


class StorePaymentInfoServiceMockFactory:
    @classmethod
    def create(cls) -> AsyncMock:
        mock = AsyncMock()
        mock.get_complete_by_store.return_value = None
        mock.get_by_store.return_value = None
        return mock


class PaymentSchedulerServiceMockFactory:
    @classmethod
    def create(cls) -> MagicMock:
        mock = MagicMock()
        mock.schedule_payment_timeout = AsyncMock(return_value=True)
        mock.remove_payment_schedule = MagicMock(return_value=True)
        return mock


class PaymentGatewayServiceMockFactory:
    @classmethod
    def create(cls) -> AsyncMock:
        mock = AsyncMock()
        mock.verify.return_value = {"amount": 10000, "payment_method": "CARD"}
        mock.refund.return_value = {"refunded": True}
        return mock


class OrderQueryServiceMockFactory:
    @classmethod
    def create(cls) -> AsyncMock:
        mock = AsyncMock()
        mock.create_cart_item.return_value = None
        mock.get_cart_item.return_value = None
        mock.delete_cart_item.return_value = True
        mock.create_order_from_cart.return_value = None
        return mock


class CustomerProfileServiceMockFactory:
    @classmethod
    def create(cls) -> AsyncMock:
        mock = AsyncMock()
        mock.get_preference_snapshot.return_value = {
            "preferred_menus": None,
            "nutrition_types": None,
            "allergies": None,
            "topping_types": None,
        }
        return mock


class BackgroundTasksFakeFactory:
    @classmethod
    def create(cls):
        tasks: list = []

        class _FakeBT:
            def add_task(self, fn, *args, **kwargs):
                tasks.append((fn, args, kwargs))

        return _FakeBT(), tasks
