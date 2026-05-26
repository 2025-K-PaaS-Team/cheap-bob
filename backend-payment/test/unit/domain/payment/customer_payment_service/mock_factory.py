"""payment-svc 분리 후 mocks — HTTP client + cart_item service 중심.

CustomerPaymentService 가 의존하는 6개:
  - uow (트랜잭션 진입점)
  - store_payment_info_service (local)
  - payment_gateway_service (PortOne)
  - cart_item_service (local cart CRUD/lock)
  - internal_seller_client (HTTP → backend.seller)
  - internal_order_client (HTTP → backend.order)
"""
from unittest.mock import AsyncMock, MagicMock
from types import SimpleNamespace


class _NestedTxCM:
    """``session.begin_nested()`` 가 반환하는 SAVEPOINT CM 의 fake."""
    def __init__(self, raise_exc: Exception | None = None):
        self._raise_exc = raise_exc


    async def __aenter__(self):
        if self._raise_exc is not None:
            raise self._raise_exc
        return None


    async def __aexit__(self, exc_type, exc, tb):
        return False


class FakeUnitOfWork:
    """@transactional 호환 fake — 한 진입에 한 session 을 공유."""
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
    session.begin_nested = MagicMock(side_effect=lambda: _NestedTxCM())
    return session


class StorePaymentInfoServiceMockFactory:
    @classmethod
    def create(cls) -> AsyncMock:
        mock = AsyncMock()
        mock.get_complete_by_store.return_value = None
        return mock


class PaymentGatewayServiceMockFactory:
    @classmethod
    def create(cls) -> AsyncMock:
        mock = AsyncMock()
        mock.verify.return_value = SimpleNamespace(
            payment_method="CARD", total_amount=10000,
        )
        mock.fetch_status.return_value = None
        mock.refund.return_value = {"refunded": True}
        return mock


class CartItemServiceMockFactory:
    @classmethod
    def create(cls) -> AsyncMock:
        mock = AsyncMock()
        mock.lock.return_value = None
        mock.get.return_value = None
        mock.delete.return_value = True
        mock.create.return_value = None
        mock.claim_expired_for_processing.return_value = []
        return mock


class InternalSellerClientMockFactory:
    """HTTP → backend.seller — find_product, get_today_operation, consume/restore_stock."""

    @classmethod
    def create(cls) -> AsyncMock:
        mock = AsyncMock()
        mock.find_product.return_value = None
        mock.get_today_operation.return_value = None
        mock.consume_stock.return_value = None
        mock.restore_stock.return_value = None
        return mock


class InternalOrderClientMockFactory:
    """HTTP → backend.order — create_order_from_cart (멱등)."""

    @classmethod
    def create(cls) -> AsyncMock:
        mock = AsyncMock()
        mock.create_order_from_cart.return_value = None
        return mock


class BackgroundTasksFakeFactory:
    @classmethod
    def create(cls):
        tasks: list = []

        class _FakeBT:
            def add_task(self, fn, *args, **kwargs):
                tasks.append((fn, args, kwargs))

        return _FakeBT(), tasks
