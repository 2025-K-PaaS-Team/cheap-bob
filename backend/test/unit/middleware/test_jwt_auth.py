"""Tests for ``app.middleware.auth.JWTAuthMiddleware``.

BaseHTTPMiddleware 의 ``dispatch`` 만 단위 검증한다. WebSocket scope 는 BaseHTTPMiddleware
가 자체적으로 우회하므로 본 단위에선 다루지 않는다 (그 보장 자체가 Starlette 책임).
"""
from unittest.mock import AsyncMock, MagicMock
from starlette.types import Receive, Scope, Send
import pytest
from datetime import datetime, timedelta, timezone

from app.middleware.auth import JWTAuthMiddleware


def _make_request(
    path: str,
    *,
    cookies: dict | None = None,
    headers: dict | None = None,
    query: str = "",
):
    """Starlette Request 객체를 직접 만든다.

    BaseHTTPMiddleware.dispatch 가 받는 인자는 Request 이므로, 모든 필드를 갖춘 scope 면
    충분하다. send/receive 는 dispatch 단계에선 호출되지 않는다.
    """
    from starlette.requests import Request

    raw_headers: list[tuple[bytes, bytes]] = []
    if cookies:
        cookie_str = "; ".join(f"{k}={v}" for k, v in cookies.items())
        raw_headers.append((b"cookie", cookie_str.encode()))
    for k, v in (headers or {}).items():
        raw_headers.append((k.lower().encode(), v.encode()))

    scope: Scope = {
        "type": "http",
        "method": "GET",
        "path": path,
        "raw_path": path.encode(),
        "query_string": query.encode(),
        "headers": raw_headers,
    }
    return Request(scope)


@pytest.fixture
def jwt_service_mock():
    """JwtService 의 ``verify_and_refresh_token`` 만 mock 한다."""
    mock = MagicMock()
    mock.verify_and_refresh_token = MagicMock(
        return_value=(True, None, {"sub": "alice@example.com", "user_type": "customer", "is_active": True}),
    )
    return mock


@pytest.fixture
def middleware(jwt_service_mock):
    # app 인자는 ASGIApp callable — dispatch 호출엔 안 쓰이지만 super().__init__ 가 받는다.
    return JWTAuthMiddleware(app=lambda *a, **kw: None, jwt_service=jwt_service_mock)


# ────────────────────────────────────────────────────────────────────
# excluded prefix
# ────────────────────────────────────────────────────────────────────

@pytest.mark.unit
class TestExcludedPrefixes:
    """auth/common/docs/health 는 토큰 없이도 통과해야 한다."""

    @pytest.mark.parametrize("path", [
        "/api/v1/auth/google/login/customer",
        "/api/v1/auth/google/callback/seller",
        "/api/v1/common/options/preferred-menus",
        "/docs",
        "/redoc",
        "/openapi.json",
        "/health",
    ])
    async def test_excluded_path_bypasses_auth(self, middleware, path, jwt_service_mock):
        request = _make_request(path)
        call_next = AsyncMock(return_value=MagicMock(name="response"))

        response = await middleware.dispatch(request, call_next)

        call_next.assert_awaited_once_with(request)
        # 토큰 검증 자체가 호출되지 않아야 한다.
        jwt_service_mock.verify_and_refresh_token.assert_not_called()


# ────────────────────────────────────────────────────────────────────
# token extraction (dev vs prod)
# ────────────────────────────────────────────────────────────────────

@pytest.mark.unit
class TestTokenExtraction:
    """``_extract_token`` — ``access_token`` 쿠키만 사용한다."""

    def test_returns_cookie_value(self, middleware):
        req = _make_request(
            "/api/v1/seller/store/orders",
            cookies={"access_token": "COOKIE_TOKEN"},
        )
        assert middleware._extract_token(req) == "COOKIE_TOKEN"


    def test_ignores_authorization_header_and_query_token(self, middleware):
        """Bearer 헤더 / ?token 쿼리는 모두 무시 — 쿠키만 인정한다."""
        req = _make_request(
            "/api/v1/seller/store/orders",
            headers={"Authorization": "Bearer HEADER_TOKEN"},
            query="token=QUERY_TOKEN",
        )
        assert middleware._extract_token(req) is None


    def test_returns_none_when_no_cookie(self, middleware):
        req = _make_request("/api/v1/seller/store/orders")
        assert middleware._extract_token(req) is None


# ────────────────────────────────────────────────────────────────────
# dispatch — 인증 분기
# ────────────────────────────────────────────────────────────────────

@pytest.mark.unit
class TestDispatchAuth:

    async def test_returns_401_when_no_token(self, middleware):
        request = _make_request("/api/v1/customer/orders")
        call_next = AsyncMock()

        response = await middleware.dispatch(request, call_next)

        assert response.status_code == 401
        call_next.assert_not_awaited()


    async def test_returns_401_when_token_invalid(self, middleware, jwt_service_mock):
        jwt_service_mock.verify_and_refresh_token.return_value = (False, None, None)
        request = _make_request(
            "/api/v1/customer/orders", cookies={"access_token": "BAD"},
        )
        response = await middleware.dispatch(request, AsyncMock())

        assert response.status_code == 401


    async def test_sets_request_state_user_on_valid_token(
        self, middleware, jwt_service_mock,
    ):
        request = _make_request(
            "/api/v1/customer/orders", cookies={"access_token": "OK"},
        )
        # call_next 가 받은 request 의 state.user 를 검증.
        captured = {}
        async def _capture(req):
            captured["user"] = req.state.user
            return MagicMock(name="response", set_cookie=MagicMock())
        await middleware.dispatch(request, _capture)

        assert captured["user"]["sub"] == "alice@example.com"


    async def test_sets_refreshed_cookie_when_returned(
        self, middleware, jwt_service_mock,
    ):
        """verify_and_refresh_token 이 새 토큰을 반환하면 응답에 set_cookie 가 호출된다."""
        jwt_service_mock.verify_and_refresh_token.return_value = (
            True, "NEW_TOKEN", {"sub": "alice@example.com", "user_type": "customer", "is_active": True},
        )
        request = _make_request(
            "/api/v1/customer/orders", cookies={"access_token": "OLD"},
        )
        response = MagicMock(name="response", set_cookie=MagicMock())
        await middleware.dispatch(request, AsyncMock(return_value=response))

        response.set_cookie.assert_called_once()
        assert response.set_cookie.call_args.kwargs["value"] == "NEW_TOKEN"
