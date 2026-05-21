from typing import Annotated, Callable, Dict, Optional, Sequence
from starlette.types import ASGIApp
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse
from fastapi import Depends, HTTPException, Request, Response, status

from app.domain.auth.service.jwt import JwtService
from app.domain.auth.dto.auth import UserType
from app.domain.auth.cookie import set_auth_cookie
from app.config.setting import settings


class JWTAuthMiddleware(BaseHTTPMiddleware):
    """JWT 인증 미들웨어.

    payload 를 `request.state.user` (dict) 에 채우고, 만료 5분 이내면 새 토큰을 cookie 에
    갱신한다. 비즈니스 분기는 라우터 (아래 require_user 팩토리) 로 위임 — 미들웨어는 인증 사실만 보장한다.
    """

    EXCLUDE_PREFIXES: Sequence[str] = (
        "/api/v1/auth/",
        "/api/v1/common/",
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
        """dev 한정 ``Authorization: Bearer`` 헤더 허용. prod 는 쿠키 only.

        ?token 쿼리 파라미터는 브라우저 히스토리/서버 로그에 토큰이 leak 되어
        지원하지 않는다 — Authorization 헤더 또는 쿠키만 사용.
        """
        if settings.ENVIRONMENT == "dev":
            authorization = request.headers.get("Authorization")
            if authorization and authorization.startswith("Bearer "):
                return authorization[7:]

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
    role: Optional[UserType] = None,
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

        if role is not None and user.get("user_type") != role.value:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"{role.value.capitalize()} 권한이 필요합니다",
            )
        return user

    return Depends(_dep)


CurrentCustomerDep = Annotated[Dict, require_user(role=UserType.CUSTOMER)]
CurrentSellerDep = Annotated[Dict, require_user(role=UserType.SELLER)]
CurrentCustomerNoActiveDep = Annotated[
    Dict, require_user(role=UserType.CUSTOMER, allow_inactive=True),
]
CurrentSellerNoActiveDep = Annotated[
    Dict, require_user(role=UserType.SELLER, allow_inactive=True),
]
