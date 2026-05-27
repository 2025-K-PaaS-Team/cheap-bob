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
    session.add = MagicMock()
    return session


class StorePaymentInfoServiceMockFactory:
    @classmethod
    def create(cls) -> AsyncMock:
        mock = AsyncMock()
        # 정상 케이스 default — 완전한 secret_key 가진 가게.
        mock.get_complete_by_store.return_value = SimpleNamespace(
            store_id="STR_x",
            portone_store_id="po_store_x",
            portone_channel_id="po_chan_x",
            portone_secret_key="po_secret_xxx",
        )
        return mock


class PaymentGatewayServiceMockFactory:
    @classmethod
    def create(cls) -> AsyncMock:
        mock = AsyncMock()
        # 정상 케이스 default — refund 성공.
        mock.refund.return_value = {"status": "success"}
        return mock


class ProcessedEventRepoMockFactory:
    @classmethod
    def create(cls) -> AsyncMock:
        mock = AsyncMock()
        # 정상 케이스 default — 처음 보는 이벤트.
        mock.try_mark.return_value = True
        return mock
