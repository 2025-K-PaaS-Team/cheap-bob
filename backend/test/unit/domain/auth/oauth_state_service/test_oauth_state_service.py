"""Tests for ``app.domain.auth.service.oauth_state.OAuthStateService``.

Redis 는 가짜 in-memory dict 로 대체하고, ``getdel`` / ``set`` 의 atomic 동작을 흉내낸다.
주요 분기:
  - issue 가 UUID 반환 + Redis set 호출
  - consume 시 user_type 일치 → True + Redis 키 삭제 (재사용 불가)
  - consume 시 user_type 불일치 → False (cross-type replay 차단)
  - consume 시 state 미존재 → False
  - 빈 state → False (early return, Redis 호출 없음)
"""
from unittest.mock import AsyncMock
import pytest

from app.domain.auth.dto.auth import UserType
from app.domain.auth.service.oauth_state import OAuthStateService


class FakeRedis:
    """``set`` / ``getdel`` 만 흉내내는 minimal fake."""

    def __init__(self):
        self.store: dict[str, str] = {}
        self.set_calls: list[tuple[str, str, int | None]] = []


    async def set(self, key: str, value: str, ex: int | None = None):
        self.store[key] = value
        self.set_calls.append((key, value, ex))


    async def getdel(self, key: str):
        return self.store.pop(key, None)


@pytest.fixture(autouse=True)
def fake_redis(monkeypatch):
    fake = FakeRedis()
    monkeypatch.setattr(
        "app.domain.auth.service.oauth_state.RedisClient.get_client",
        AsyncMock(return_value=fake),
    )
    return fake


@pytest.mark.unit
class TestIssue:

    async def test_returns_uuid_hex_and_stores_user_type(self, fake_redis):
        state = await OAuthStateService.issue(UserType.CUSTOMER)
        assert isinstance(state, str) and len(state) == 32  # uuid4 hex
        assert fake_redis.store[f"oauth:state:{state}"] == "customer"


    async def test_sets_ttl(self, fake_redis):
        await OAuthStateService.issue(UserType.SELLER)
        assert len(fake_redis.set_calls) == 1
        _key, value, ttl = fake_redis.set_calls[0]
        assert value == "seller"
        assert ttl == 5 * 60


@pytest.mark.unit
class TestConsume:

    async def test_matching_user_type_returns_true_and_deletes(self, fake_redis):
        state = await OAuthStateService.issue(UserType.CUSTOMER)
        assert await OAuthStateService.consume(state, expected_type=UserType.CUSTOMER) is True
        # 재사용 차단 — 이미 GETDEL 로 제거됨.
        assert f"oauth:state:{state}" not in fake_redis.store


    async def test_cross_type_replay_blocked(self, fake_redis):
        """customer login 으로 발급된 state 를 seller callback 에 재사용 시도 차단."""
        state = await OAuthStateService.issue(UserType.CUSTOMER)
        assert await OAuthStateService.consume(state, expected_type=UserType.SELLER) is False


    async def test_missing_state_returns_false(self, fake_redis):
        assert await OAuthStateService.consume("nonexistent", expected_type=UserType.CUSTOMER) is False


    async def test_empty_state_returns_false_early(self, fake_redis):
        assert await OAuthStateService.consume("", expected_type=UserType.CUSTOMER) is False
        assert await OAuthStateService.consume(None, expected_type=UserType.CUSTOMER) is False  # type: ignore[arg-type]


    async def test_consume_is_one_shot(self, fake_redis):
        """같은 state 두 번 consume 하면 첫번째만 통과 (atomic GETDEL)."""
        state = await OAuthStateService.issue(UserType.CUSTOMER)
        assert await OAuthStateService.consume(state, expected_type=UserType.CUSTOMER) is True
        assert await OAuthStateService.consume(state, expected_type=UserType.CUSTOMER) is False
