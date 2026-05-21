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


class CustomerAccountServiceMockFactory:
    @classmethod
    def create(cls) -> AsyncMock:
        mock = AsyncMock()
        mock.find_by_email.return_value = None
        # create 는 신규 row 를 그대로 만들어 반환 (실서비스 시그니처 모사).
        mock.create.side_effect = lambda email: SimpleNamespace(
            email=email, is_active=True,
        )
        return mock


class SellerAccountServiceMockFactory:
    @classmethod
    def create(cls) -> AsyncMock:
        mock = AsyncMock()
        mock.find_by_email.return_value = None
        mock.create.side_effect = lambda email: SimpleNamespace(
            email=email, is_active=True,
        )
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
