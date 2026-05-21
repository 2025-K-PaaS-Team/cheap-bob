"""Tests for ``app.domain.auth.service.jwt.JwtService``."""
from datetime import datetime, timedelta, timezone
from jose import jwt
import pytest

from app.config.setting import settings


@pytest.mark.unit
class TestCreateAccessToken:
    """JwtService.create_access_token 의 페이로드/만료 정책."""

    def test_includes_user_type_iat_exp(self, service):
        token = service.create_access_token(
            data={"sub": "alice@example.com"}, user_type="customer",
        )

        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        assert payload["sub"] == "alice@example.com"
        assert payload["user_type"] == "customer"
        assert "iat" in payload and "exp" in payload
        assert payload["exp"] > payload["iat"]


    def test_does_not_mutate_input_dict(self, service):
        data = {"sub": "alice@example.com"}
        service.create_access_token(data=data, user_type="customer")

        # 원본 dict 가 변형되면 호출자가 예상치 못한 user_type 을 보게 된다.
        assert "user_type" not in data
        assert "exp" not in data


@pytest.mark.unit
class TestDecodeAccessToken:

    def test_returns_payload_for_valid_token(self, service):
        token = service.create_user_token(
            email="alice@example.com", user_type="customer", is_active=True,
        )

        payload = service.decode_access_token(token)

        assert payload is not None
        assert payload["sub"] == "alice@example.com"
        assert payload["user_type"] == "customer"
        assert payload["is_active"] is True


    def test_returns_none_for_malformed_token(self, service):
        assert service.decode_access_token("not-a-token") is None


    def test_returns_none_for_token_signed_with_other_secret(self, service):
        bad_token = jwt.encode(
            {"sub": "alice@example.com", "exp": datetime.now(timezone.utc) + timedelta(hours=1)},
            "wrong-secret",
            algorithm=settings.JWT_ALGORITHM,
        )
        assert service.decode_access_token(bad_token) is None


@pytest.mark.unit
class TestCreateUserToken:

    def test_includes_is_active_flag(self, service):
        token = service.create_user_token(
            email="bob@example.com", user_type="seller", is_active=False,
        )
        payload = service.decode_access_token(token)
        assert payload["is_active"] is False
        assert payload["user_type"] == "seller"


@pytest.mark.unit
class TestVerifyAndRefreshToken:
    """만료까지 5분 이상 — 갱신 없음 / 5분 이내 — 새 토큰 반환 / 만료 — invalid."""

    def test_valid_long_lived_token_no_refresh(self, service):
        token = service.create_user_token(
            email="alice@example.com", user_type="customer", is_active=True,
        )

        valid, refreshed, payload = service.verify_and_refresh_token(token)

        assert valid is True
        assert refreshed is None
        assert payload["sub"] == "alice@example.com"


    def test_expired_token_returns_invalid(self, service):
        now = datetime.now(timezone.utc)
        expired = jwt.encode(
            {
                "sub": "alice@example.com",
                "user_type": "customer",
                "is_active": True,
                "iat": now - timedelta(hours=2),
                "exp": now - timedelta(minutes=1),
            },
            settings.JWT_SECRET,
            algorithm=settings.JWT_ALGORITHM,
        )

        valid, refreshed, payload = service.verify_and_refresh_token(expired)

        assert valid is False
        assert refreshed is None
        assert payload is None


    def test_token_near_expiry_is_refreshed(self, service):
        """만료 5분 이내면 새 토큰을 함께 반환한다 (rolling session)."""
        now = datetime.now(timezone.utc)
        about_to_expire = jwt.encode(
            {
                "sub": "alice@example.com",
                "user_type": "customer",
                "is_active": True,
                "iat": now - timedelta(minutes=55),
                "exp": now + timedelta(minutes=2),  # < 5분
            },
            settings.JWT_SECRET,
            algorithm=settings.JWT_ALGORITHM,
        )

        valid, refreshed, payload = service.verify_and_refresh_token(about_to_expire)

        assert valid is True
        assert refreshed is not None
        # 새 토큰의 exp 가 원본보다 미래여야 한다.
        new_payload = service.decode_access_token(refreshed)
        assert new_payload["exp"] > payload["exp"]
        assert new_payload["sub"] == "alice@example.com"
        assert new_payload["user_type"] == "customer"
        assert new_payload["is_active"] is True


    def test_malformed_token_returns_invalid(self, service):
        valid, refreshed, payload = service.verify_and_refresh_token("garbage")
        assert valid is False
        assert refreshed is None
        assert payload is None
