"""OAuth CSRF state token Redis 관리.

OAuth state 흐름 (https://datatracker.ietf.org/doc/html/rfc6749#section-10.12):
  1. /login 진입 시 서버가 UUID state 발급 → Redis 에 user_type 저장 (5분 TTL)
  2. provider authorize URL 로 redirect, state 동봉
  3. provider 가 /callback 으로 redirect 시 state 그대로 echo
  4. /callback 에서 ``OAuthStateService.consume`` 으로 GETDEL atomic 검증 → 일치하지
     않으면 CSRF 시도로 거부

state 에 user_type 까지 묶는 이유: customer login 으로 발급된 state 를 seller callback
에서 재사용하는 cross-type replay 도 차단.
"""
import uuid
from typing import Optional

from app.domain.auth.dto.auth import UserType
from app.core.redis import RedisClient


_KEY_PREFIX = "oauth:state:"
_TTL_SECONDS = 5 * 60  # OAuth provider 왕복 시간 + 사용자 입력 여유.

# dev 환경의 frontend 로컬 분기용 매직값 — login 에서 state 발급을 건너뛰고
# callback 에서 CSRF 검증을 우회한다. ENVIRONMENT=dev 일 때만 효력 있음.
DEV_LOCAL_STATE = "1004"


class OAuthStateService:

    @classmethod
    def _key(cls, state: str) -> str:
        return f"{_KEY_PREFIX}{state}"


    @classmethod
    async def issue(cls, user_type: UserType) -> str:
        """state UUID 발급 + Redis 에 expected user_type 저장."""
        state = uuid.uuid4().hex
        redis = await RedisClient.get_client()
        await redis.set(cls._key(state), user_type.value, ex=_TTL_SECONDS)
        return state


    @classmethod
    async def consume(cls, state: Optional[str], *, expected_type: UserType) -> bool:
        """state 가 expected_type 으로 발급됐는지 검증 + atomic 삭제.

        Returns:
            True  — Redis 에 존재하고 user_type 일치. 같은 state 재사용은 불가능 (GETDEL).
            False — 미존재 / 만료 / user_type 불일치. CSRF 시도 또는 만료.
        """
        if not state:
            return False
        redis = await RedisClient.get_client()
        value = await redis.getdel(cls._key(state))
        if value is None:
            return False
        return value == expected_type.value
