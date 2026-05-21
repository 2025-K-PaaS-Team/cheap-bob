from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock


class FakeAsyncContextManager:
    """`async with` 프로토콜만 지원하는 단순한 가짜 컨텍스트매니저."""

    def __init__(self, inner):
        self._inner = inner


    async def __aenter__(self):
        return self._inner


    async def __aexit__(self, exc_type, exc, tb):
        return False


class FakeUnitOfWork:
    """`@transactional` 의 ``async with self.uow as session:`` 를 만족."""

    def __init__(self, session):
        self._session = session


    async def __aenter__(self):
        return self._session


    async def __aexit__(self, exc_type, exc, tb):
        return False


def make_mock_session() -> MagicMock:
    """서비스가 ``self._session`` 으로 접근하는 메서드만 Mock 으로 채워준다."""
    session = MagicMock(name="session")
    session.flush = AsyncMock()
    session.refresh = AsyncMock()
    return session


class CustomerRepositoryMockFactory:
    @classmethod
    def create(cls) -> AsyncMock:
        mock = AsyncMock()
        mock.find_by_email.return_value = None
        # save 는 입력받은 인스턴스를 그대로 돌려준다 (실 레포지토리 시그니처 모사).
        mock.save.side_effect = lambda customer: customer
        return mock


class SellerRepositoryMockFactory:
    @classmethod
    def create(cls) -> AsyncMock:
        mock = AsyncMock()
        mock.find_by_email.return_value = None
        mock.save.side_effect = lambda seller: seller
        return mock


class JwtServiceMockFactory:
    @classmethod
    def create(cls) -> MagicMock:
        mock = MagicMock()
        mock.create_user_token = MagicMock(return_value="JWT_TOKEN_STUB")
        return mock


def make_oauth_client_mock(email: str | None = "user@example.com"):
    """``create_oauth_client(provider)`` 가 반환하는 async-context-manager mock.

    내부 client 의 ``get_access_token`` / ``get_user_info`` 가 우리가 정한 값을 반환하게 한다.
    """
    inner = MagicMock(name="oauth_client_inner")
    inner.get_access_token = AsyncMock(return_value="ACCESS_TOKEN_STUB")
    inner.get_user_info = AsyncMock(
        return_value=SimpleNamespace(email=email, raw={}),
    )
    return FakeAsyncContextManager(inner), inner
