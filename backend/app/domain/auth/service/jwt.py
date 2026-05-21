from typing import Dict, Optional, Tuple
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone

from app.config.setting import settings


# 본 시스템이 발급하는 토큰의 필수 클레임. 누락된 토큰은 변조/구버전으로 간주하고 거부한다.
_REQUIRED_CLAIMS = frozenset({"sub", "user_type", "is_active", "exp"})


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
        """서명/만료/필수 클레임을 모두 통과한 payload 만 반환. 그 외는 None.

        필수 클레임 검증을 여기 한곳에 모아두면, 호출처에서 `payload["sub"]` 같은
        직접 인덱싱이 KeyError → 500 으로 새지 않는다.
        """
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
        """토큰을 검증하고 만료 5분 이내면 새 토큰을 함께 반환한다.

        Returns:
            (valid, refreshed_token_or_none, payload_or_none)
        """
        payload = self.decode_access_token(token)
        if payload is None:
            return False, None, None

        # exp 는 _REQUIRED_CLAIMS 가 보장. jwt.decode 가 이미 만료를 검증하므로
        # 본 분기는 refresh window 계산용으로만 사용한다.
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
