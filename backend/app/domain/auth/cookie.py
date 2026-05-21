"""access_token 쿠키 발급/갱신/제거 단일 진입점.

callback / logout / middleware refresh 가 모두 본 helper 를 거치도록 통일한다.
각자 `set_cookie(...)` 를 직접 호출하면 SameSite / max_age / path 정책이 갈라져
"발급은 SameSite=None 으로 했는데 refresh 가 Lax 로 덮어써서 dev cross-site 흐름이 끊긴다"
같은 사고가 난다.
"""
from fastapi import Response

from app.config.setting import settings


_COOKIE_KEY = "access_token"


def _samesite() -> str:
    """dev 는 cross-site 호환을 위해 None, 그 외 환경은 CSRF 위험을 줄여 Lax."""
    return "none" if settings.ENVIRONMENT == "dev" else "lax"


def set_auth_cookie(response: Response, token: str) -> None:
    """access_token 발급/갱신."""
    response.set_cookie(
        key=_COOKIE_KEY,
        value=token,
        httponly=True,
        secure=True,
        samesite=_samesite(),
        max_age=settings.COOKIE_EXPIRE_SECONDS,
        path="/",
    )


def clear_auth_cookie(response: Response) -> None:
    """access_token 제거. samesite 는 발급 시점과 동일하게 맞춰야 브라우저가 삭제한다."""
    response.set_cookie(
        key=_COOKIE_KEY,
        value="",
        httponly=True,
        secure=True,
        samesite=_samesite(),
        max_age=0,
        path="/",
    )
