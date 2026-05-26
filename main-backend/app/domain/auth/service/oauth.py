import httpx

from app.domain.seller.service.seller_account import SellerAccountService
from app.domain.customer.service.customer_account import CustomerAccountService
from app.domain.auth.service.jwt import JwtService
from app.domain.auth.service.exception import (
    OAuthAuthenticationError,
    OAuthEmailMissingError,
)
from app.domain.auth.dto.auth import AuthResult, UserType
from app.core.oauth import create_oauth_client
from app.config.oauth import OAuthProvider


class OAuthService:
    """OAuth 인증 흐름 전체 (provider 호출 + JWT 발급 + 신규 가입 처리).

    customer / seller row 의 CRUD 는 직접 다루지 않고 각 도메인의 AccountService 에
    위임한다 (strict service-to-service — auth 가 customer/seller model/repo 를 직접
    import 하지 않음).
    """

    def __init__(
        self,
        jwt_service: JwtService,
        customer_account_service: CustomerAccountService,
        seller_account_service: SellerAccountService,
    ):
        self.jwt_service = jwt_service
        self.customer_account_service = customer_account_service
        self.seller_account_service = seller_account_service


    async def authenticate(
        self,
        *,
        provider: OAuthProvider,
        code: str,
        requested_type: UserType,
    ) -> AuthResult:
        """code → access_token → user info → JWT 발급.

        OAuth provider 호출은 외부 I/O 라 트랜잭션 밖에서 수행한다. DB 작업 (가입/조회)
        은 각 AccountService 가 자체 트랜잭션으로 처리한다.

        provider 통신 실패는 `OAuthAuthenticationError`, email 누락은
        `OAuthEmailMissingError` 로 정규화한다 (callback 라우터가 단일 except 로 잡아
        프론트 error 페이지로 분기). DB / 내부 오류는 그대로 throw 되어 글로벌 핸들러로 간다.
        """
        try:
            async with create_oauth_client(provider) as oauth_client:
                access_token = await oauth_client.get_access_token(
                    code, requested_type.value,
                )
                oauth_user = await oauth_client.get_user_info(access_token)
        except httpx.HTTPError as e:
            raise OAuthAuthenticationError(
                f"{provider.value} OAuth 통신 실패: {e}",
            ) from e

        if not oauth_user.email:
            raise OAuthEmailMissingError(
                f"{provider.value} 가 email 을 제공하지 않았습니다",
            )

        return await self._resolve_and_issue(
            email=oauth_user.email,
            requested_type=requested_type,
        )


    async def _resolve_and_issue(
        self, *, email: str, requested_type: UserType,
    ) -> AuthResult:
        # 반대 타입으로 이미 가입돼 있으면 충돌. 토큰은 *실제 가입 종류* 기준으로 발급.
        # 일치하는 타입은 멱등한 `find_or_create` 로 한 번에 보장 — 동시 콜백 race 안전.
        if requested_type == UserType.CUSTOMER:
            seller = await self.seller_account_service.find_by_email(email)
            if seller is not None:
                return self._issue(
                    email=email,
                    actual_type=UserType.SELLER,
                    is_active=seller.is_active,
                    conflict=True,
                )
            customer = await self.customer_account_service.find_or_create(email)
            return self._issue(
                email=email,
                actual_type=UserType.CUSTOMER,
                is_active=customer.is_active,
                conflict=False,
            )

        # requested_type == UserType.SELLER
        customer = await self.customer_account_service.find_by_email(email)
        if customer is not None:
            return self._issue(
                email=email,
                actual_type=UserType.CUSTOMER,
                is_active=customer.is_active,
                conflict=True,
            )
        seller = await self.seller_account_service.find_or_create(email)
        return self._issue(
            email=email,
            actual_type=UserType.SELLER,
            is_active=seller.is_active,
            conflict=False,
        )


    def _issue(
        self,
        *,
        email: str,
        actual_type: UserType,
        is_active: bool,
        conflict: bool,
    ) -> AuthResult:
        token = self.jwt_service.create_user_token(
            email=email,
            user_type=actual_type.value,
            is_active=is_active,
        )
        return AuthResult(
            access_token=token,
            user_type=actual_type,
            is_active=is_active,
            conflict=conflict,
            email=email,
        )
