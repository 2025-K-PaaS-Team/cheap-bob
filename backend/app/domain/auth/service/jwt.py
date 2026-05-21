from typing import Dict, Optional, Tuple
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone

from app.config.setting import settings


class JwtService:
    """JWT 발급 / 검증 / 갱신.

    상태가 없는 stateless 서비스이므로 컨테이너에서 `Singleton` 으로 선언한다.
    """

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
            return jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
        except JWTError:
            return None


    def create_user_token(self, email: str, user_type: str, is_active: bool) -> str:
        return self.create_access_token(
            data={"sub": email, "is_active": is_active},
            user_type=user_type,
        )


    def verify_and_refresh_token(
        self, token: str,
    ) -> Tuple[bool, Optional[str], Optional[Dict]]:
        """토큰을 검증하고 만료 5분 이내면 새 토큰을 함께 반환한다.

        Returns:
            (valid, refreshed_token_or_none, payload_or_none)
        """
        payload = self.decode_access_token(token)
        if not payload:
            return False, None, None

        exp = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
        now = datetime.now(timezone.utc)
        if exp < now:
            return False, None, None

        if exp - now < timedelta(minutes=5):
            refreshed = self.create_user_token(
                email=payload["sub"],
                user_type=payload["user_type"],
                is_active=payload["is_active"],
            )
            return True, refreshed, payload

        return True, None, payload
