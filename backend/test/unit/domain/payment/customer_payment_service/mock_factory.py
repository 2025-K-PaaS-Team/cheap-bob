from unittest.mock import AsyncMock, MagicMock


class _NestedTxCM:
    """``session.begin_nested()`` 가 반환하는 SAVEPOINT context manager 의 fake.

    인자 ``raise_exc`` 가 주어지면 __aenter__ 직후 그 예외를 발생시켜 outer 코드의
    swallow 동작을 검증한다.
    """
    def __init__(self, raise_exc: Exception | None = None):
        self._raise_exc = raise_exc


    async def __aenter__(self):
        if self._raise_exc is not None:
            raise self._raise_exc
        return None


    async def __aexit__(self, exc_type, exc, tb):
        # 실제 begin_nested 는 SAVEPOINT 를 자동 롤백 — 본 fake 는 단순 swallow 흉내.
        return False


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
    # ``session.begin_nested()`` 는 SAVEPOINT context manager 를 동기 반환.
    # 기본값은 정상 enter/exit; 테스트별로 ``side_effect`` 로 덮어쓸 수 있다.
    session.begin_nested = MagicMock(side_effect=lambda: _NestedTxCM())
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


class PaymentGatewayServiceMockFactory:
    @classmethod
    def create(cls) -> AsyncMock:
        from types import SimpleNamespace

        mock = AsyncMock()
        # verify 는 PortOnePayment-like 객체 반환 (실제 dataclass 대신 SimpleNamespace 로 가볍게).
        mock.verify.return_value = SimpleNamespace(
            payment_method="CARD", total_amount=10000,
        )
        # fetch_status 의 기본값은 None — "PortOne 에 결제 기록 없음" 을 의미. 테스트별로
        # PAID/FAILED 등 PortOnePayment-like 객체로 덮어쓴다.
        mock.fetch_status.return_value = None
        mock.refund.return_value = {"refunded": True}
        return mock


class OrderQueryServiceMockFactory:
    @classmethod
    def create(cls) -> AsyncMock:
        mock = AsyncMock()
        mock.create_cart_item.return_value = None
        mock.get_cart_item.return_value = None
        mock.lock_cart_item.return_value = None
        mock.delete_cart_item.return_value = True
        mock.create_order_from_cart.return_value = None
        return mock


class CartItemRepoMockFactory:
    """``sweep_expired_carts`` 가 service 내부에서 직접 ``CartItemRepository(self._session)`` 를
    construct 하므로, 본 mock 은 ``app.domain.order.repository.cart_item.CartItemRepository`` 자체를
    monkeypatch 로 교체할 때 사용한다."""

    @classmethod
    def create(cls) -> AsyncMock:
        mock = AsyncMock()
        mock.claim_expired_for_processing.return_value = []
        mock.delete.return_value = True
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
