"""payment-svc 자체 JWT 미들웨어.

backend 와 동일한 JWT_SECRET 으로 cookie 를 검증한다. 따라서 frontend → payment-svc 직접
호출에서도 동일한 인증 모델이 동작한다. backend 와 코드 중복은 의도적 — shared 패턴
미적용 정책.
"""
from typing import Annotated, Callable, Dict, Optional, Sequence
from starlette.types import ASGIApp
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse
from fastapi import Depends, HTTPException, Request, Response, status

from app.core.auth import JwtService, set_auth_cookie


class JWTAuthMiddleware(BaseHTTPMiddleware):
    """JWT 인증 미들웨어. /api/internal/* 와 /health, /docs 등은 제외."""

    EXCLUDE_PREFIXES: Sequence[str] = (
        "/api/internal/",
        "/docs",
        "/redoc",
        "/openapi.json",
        "/health",
    )


    def __init__(self, app: ASGIApp, jwt_service: JwtService) -> None:
        super().__init__(app)
        self.jwt_service = jwt_service


    def _is_excluded(self, path: str) -> bool:
        return any(path.startswith(prefix) for prefix in self.EXCLUDE_PREFIXES)


    def _extract_token(self, request: Request) -> Optional[str]:
        return request.cookies.get("access_token")


    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if self._is_excluded(request.url.path):
            return await call_next(request)

        token = self._extract_token(request)
        if not token:
            return JSONResponse(status_code=401, content={"detail": "인증이 필요합니다."})

        valid, refreshed, payload = self.jwt_service.verify_and_refresh_token(token)
        if not valid:
            return JSONResponse(status_code=401, content={"detail": "유효하지 않은 토큰입니다."})

        request.state.user = payload

        response = await call_next(request)
        if refreshed:
            set_auth_cookie(response, refreshed)
        return response


def require_user(
    *,
    role: Optional[str] = None,
    allow_inactive: bool = False,
):
    """라우터용 인증/인가 디펜던시 팩토리.

    Check 순서: 401 (state.user 누락) → 439 (탈퇴) → 403 (역할 불일치).
    """

    async def _dep(request: Request) -> Dict:
        if not hasattr(request.state, "user"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="인증이 필요합니다",
                headers={"WWW-Authenticate": "Bearer"},
            )
        user = request.state.user

        if not allow_inactive and not user.get("is_active"):
            raise HTTPException(
                status_code=439,
                detail="탈퇴한 계정입니다",
                headers={"X-Account-Status": "inactive"},
            )

        if role is not None and user.get("user_type") != role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"{role.capitalize()} 권한이 필요합니다",
            )
        return user

    return Depends(_dep)


CurrentCustomerDep = Annotated[Dict, require_user(role="customer")]
CurrentSellerDep = Annotated[Dict, require_user(role="seller")]
