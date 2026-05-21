"""Tests for ``app.domain.auth.service.oauth.OAuthService``."""
import pytest

from app.config.oauth import OAuthProvider
from app.domain.auth.dto.auth import UserType
from app.domain.auth.model.customer import Customer
from app.domain.auth.model.seller import Seller
from app.domain.auth.service.exception import OAuthEmailMissingError

from test.unit.domain.auth.oauth_service.mock_factory import make_oauth_client_mock


# ────────────────────────────────────────────────────────────────────
# authenticate — OAuth provider 호출 단계
# ────────────────────────────────────────────────────────────────────

@pytest.mark.unit
class TestAuthenticateProviderCall:
    """OAuth provider 호출 결과에 따른 분기."""

    async def test_raises_when_provider_returns_no_email(
        self, monkeypatch, service,
    ):
        ctx, _ = make_oauth_client_mock(email=None)
        monkeypatch.setattr(
            "app.domain.auth.service.oauth.create_oauth_client", lambda provider: ctx,
        )

        with pytest.raises(OAuthEmailMissingError):
            await service.authenticate(
                provider=OAuthProvider.GOOGLE,
                code="oauth-code",
                requested_type=UserType.CUSTOMER,
            )


    async def test_provider_is_invoked_with_code_and_requested_type(
        self, monkeypatch, service,
    ):
        ctx, inner = make_oauth_client_mock(email="alice@example.com")
        monkeypatch.setattr(
            "app.domain.auth.service.oauth.create_oauth_client", lambda provider: ctx,
        )

        await service.authenticate(
            provider=OAuthProvider.GOOGLE,
            code="code-xyz",
            requested_type=UserType.CUSTOMER,
        )

        inner.get_access_token.assert_awaited_once_with("code-xyz", "customer")
        inner.get_user_info.assert_awaited_once_with("ACCESS_TOKEN_STUB")


# ────────────────────────────────────────────────────────────────────
# requested=CUSTOMER 분기
# ────────────────────────────────────────────────────────────────────

@pytest.mark.unit
class TestAuthenticateAsCustomer:

    async def test_creates_new_customer_when_not_exists(
        self, monkeypatch, service, customer_repo_mock, seller_repo_mock, jwt_service_mock,
    ):
        ctx, _ = make_oauth_client_mock(email="new@example.com")
        monkeypatch.setattr(
            "app.domain.auth.service.oauth.create_oauth_client", lambda provider: ctx,
        )
        customer_repo_mock.find_by_email.return_value = None
        seller_repo_mock.find_by_email.return_value = None

        result = await service.authenticate(
            provider=OAuthProvider.GOOGLE,
            code="code",
            requested_type=UserType.CUSTOMER,
        )

        # 새 Customer 저장됐는지 확인.
        customer_repo_mock.save.assert_awaited_once()
        saved_arg = customer_repo_mock.save.call_args.args[0]
        assert isinstance(saved_arg, Customer)
        assert saved_arg.email == "new@example.com"

        assert result.email == "new@example.com"
        assert result.user_type == UserType.CUSTOMER
        assert result.is_active is True
        assert result.conflict is False
        jwt_service_mock.create_user_token.assert_called_once_with(
            email="new@example.com", user_type="customer", is_active=True,
        )


    async def test_reuses_existing_customer_with_is_active_preserved(
        self, monkeypatch, service, customer_repo_mock, seller_repo_mock,
    ):
        ctx, _ = make_oauth_client_mock(email="existing@example.com")
        monkeypatch.setattr(
            "app.domain.auth.service.oauth.create_oauth_client", lambda provider: ctx,
        )
        seller_repo_mock.find_by_email.return_value = None
        # 탈퇴 예약 상태 (is_active=False) 인 고객을 가정.
        existing = Customer(email="existing@example.com", is_active=False)
        customer_repo_mock.find_by_email.return_value = existing

        result = await service.authenticate(
            provider=OAuthProvider.GOOGLE,
            code="code",
            requested_type=UserType.CUSTOMER,
        )

        customer_repo_mock.save.assert_not_called()
        assert result.user_type == UserType.CUSTOMER
        assert result.is_active is False  # 탈퇴 상태가 유지됨
        assert result.conflict is False


    async def test_returns_conflict_when_already_registered_as_seller(
        self, monkeypatch, service, customer_repo_mock, seller_repo_mock, jwt_service_mock,
    ):
        """seller 로 가입된 email 이 customer 로 요청 — actual_type=SELLER + conflict=True."""
        ctx, _ = make_oauth_client_mock(email="dup@example.com")
        monkeypatch.setattr(
            "app.domain.auth.service.oauth.create_oauth_client", lambda provider: ctx,
        )
        seller_repo_mock.find_by_email.return_value = Seller(
            email="dup@example.com", is_active=True,
        )

        result = await service.authenticate(
            provider=OAuthProvider.GOOGLE,
            code="code",
            requested_type=UserType.CUSTOMER,
        )

        assert result.conflict is True
        assert result.user_type == UserType.SELLER
        assert result.is_active is True
        # customer 쪽은 조회조차 하지 않아야 한다.
        customer_repo_mock.find_by_email.assert_not_called()
        customer_repo_mock.save.assert_not_called()
        jwt_service_mock.create_user_token.assert_called_once_with(
            email="dup@example.com", user_type="seller", is_active=True,
        )


# ────────────────────────────────────────────────────────────────────
# requested=SELLER 분기
# ────────────────────────────────────────────────────────────────────

@pytest.mark.unit
class TestAuthenticateAsSeller:

    async def test_creates_new_seller_when_not_exists(
        self, monkeypatch, service, customer_repo_mock, seller_repo_mock,
    ):
        ctx, _ = make_oauth_client_mock(email="newseller@example.com")
        monkeypatch.setattr(
            "app.domain.auth.service.oauth.create_oauth_client", lambda provider: ctx,
        )
        customer_repo_mock.find_by_email.return_value = None
        seller_repo_mock.find_by_email.return_value = None

        result = await service.authenticate(
            provider=OAuthProvider.GOOGLE,
            code="code",
            requested_type=UserType.SELLER,
        )

        seller_repo_mock.save.assert_awaited_once()
        saved_arg = seller_repo_mock.save.call_args.args[0]
        assert isinstance(saved_arg, Seller)
        assert saved_arg.email == "newseller@example.com"
        assert result.user_type == UserType.SELLER
        assert result.is_active is True
        assert result.conflict is False


    async def test_returns_conflict_when_already_registered_as_customer(
        self, monkeypatch, service, customer_repo_mock, seller_repo_mock,
    ):
        ctx, _ = make_oauth_client_mock(email="dupc@example.com")
        monkeypatch.setattr(
            "app.domain.auth.service.oauth.create_oauth_client", lambda provider: ctx,
        )
        customer_repo_mock.find_by_email.return_value = Customer(
            email="dupc@example.com", is_active=True,
        )

        result = await service.authenticate(
            provider=OAuthProvider.GOOGLE,
            code="code",
            requested_type=UserType.SELLER,
        )

        assert result.conflict is True
        assert result.user_type == UserType.CUSTOMER
        seller_repo_mock.find_by_email.assert_not_called()
        seller_repo_mock.save.assert_not_called()
