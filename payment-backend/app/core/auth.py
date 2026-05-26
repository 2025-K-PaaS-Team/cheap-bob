"""JWT 발급/검증 + access_token 쿠키 발급 — payment-backend 자체 구현.

main-backend 와 코드 중복은 의도적 (shared 패턴 미적용). JWT_SECRET 은 env 로 공유되어
양 서비스가 같은 cookie 를 검증한다.
"""
from typing import Dict, Optional, Tuple
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from fastapi import Response

from app.config.setting import settings


_REQUIRED_CLAIMS = frozenset({"sub", "user_type", "is_active", "exp"})
_COOKIE_KEY = "access_token"


class JwtService:
    """JWT 발급/검증/갱신. stateless."""

    def __init__(self):
        self.secret_key = settings.JWT_SECRET
        self.algorithm = settings.JWT_ALGORITHM
        self.expire_minutes = settings.JWT_EXPIRE_MINUTES


    def create_access_token(self, data: Dict, user_type: str) -> str:
        to_encode = data.copy()
        now = datetime.now(timezone.utc)
        to_encode.update({
            "exp": now + timedelta(minutes=self.expire_minutes),
            "iat": now,
            "user_type": user_type,
        })
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)


    def decode_access_token(self, token: str) -> Optional[Dict]:
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
        except JWTError:
            return None
        if not _REQUIRED_CLAIMS.issubset(payload):
            return None
        return payload


    def create_user_token(self, email: str, user_type: str, is_active: bool) -> str:
        return self.create_access_token(
            data={"sub": email, "is_active": is_active},
            user_type=user_type,
        )


    def verify_and_refresh_token(
        self, token: str,
    ) -> Tuple[bool, Optional[str], Optional[Dict]]:
        payload = self.decode_access_token(token)
        if payload is None:
            return False, None, None

        exp = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
        now = datetime.now(timezone.utc)

        if exp - now < timedelta(minutes=5):
            refreshed = self.create_user_token(
                email=payload["sub"],
                user_type=payload["user_type"],
                is_active=payload["is_active"],
            )
            return True, refreshed, payload

        return True, None, payload


def _samesite() -> str:
    return "none" if settings.ENVIRONMENT == "dev" else "lax"


def set_auth_cookie(response: Response, token: str) -> None:
    """access_token 발급/갱신. main-backend 와 동일 정책."""
    response.set_cookie(
        key=_COOKIE_KEY,
        value=token,
        httponly=True,
        secure=True,
        samesite=_samesite(),
        max_age=settings.COOKIE_EXPIRE_SECONDS,
        path="/",
    )
