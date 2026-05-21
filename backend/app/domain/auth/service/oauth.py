from app.domain.auth.service.jwt import JwtService
from app.domain.auth.service.exception import OAuthEmailMissingError
from app.domain.auth.repository.seller import SellerRepository
from app.domain.auth.repository.customer import CustomerRepository
from app.domain.auth.model.seller import Seller
from app.domain.auth.model.customer import Customer
from app.domain.auth.dto.auth import AuthResult, UserType
from app.database.session import UnitOfWork, transactional
from app.core.oauth import create_oauth_client
from app.config.oauth import OAuthProvider


class OAuthService:
    """OAuth 인증 흐름 전체 (provider 호출 + JWT 발급 + 신규 가입 처리)."""

    def __init__(self, uow: UnitOfWork, jwt_service: JwtService):
        self.uow = uow
        self.jwt_service = jwt_service


    async def authenticate(
        self,
        *,
        provider: OAuthProvider,
        code: str,
        requested_type: UserType,
    ) -> AuthResult:
        """code → access_token → user info → JWT 발급.

        OAuth provider 호출은 외부 I/O 라 트랜잭션 밖에서 수행한다. DB 작업 (가입/조회)
        만 트랜잭션 안에서 처리해야 lock 점유 시간이 늘어나지 않는다.
        """
        async with create_oauth_client(provider) as oauth_client:
            access_token = await oauth_client.get_access_token(code, requested_type.value)
            oauth_user = await oauth_client.get_user_info(access_token)

        if not oauth_user.email:
            raise OAuthEmailMissingError(
                f"{provider.value} 가 email 을 제공하지 않았습니다",
            )

        return await self._resolve_and_issue(
            email=oauth_user.email,
            requested_type=requested_type,
        )


    @transactional
    async def _resolve_and_issue(
        self, *, email: str, requested_type: UserType,
    ) -> AuthResult:
        customer_repo = CustomerRepository(self._session)
        seller_repo = SellerRepository(self._session)

        if requested_type == UserType.CUSTOMER:
            # 반대 타입으로 이미 가입돼 있으면 충돌. 토큰은 *실제 가입 종류* 기준으로 발급.
            seller = await seller_repo.find_by_email(email)
            if seller is not None:
                return self._issue(
                    email=email,
                    actual_type=UserType.SELLER,
                    is_active=seller.is_active,
                    conflict=True,
                )

            customer = await customer_repo.find_by_email(email)
            if customer is None:
                customer = await customer_repo.save(Customer(email=email))
                is_active = True
            else:
                is_active = customer.is_active

            return self._issue(
                email=email,
                actual_type=UserType.CUSTOMER,
                is_active=is_active,
                conflict=False,
            )

        # requested_type == UserType.SELLER
        customer = await customer_repo.find_by_email(email)
        if customer is not None:
            return self._issue(
                email=email,
                actual_type=UserType.CUSTOMER,
                is_active=customer.is_active,
                conflict=True,
            )

        seller = await seller_repo.find_by_email(email)
        if seller is None:
            seller = await seller_repo.save(Seller(email=email))
            is_active = True
        else:
            is_active = seller.is_active

        return self._issue(
            email=email,
            actual_type=UserType.SELLER,
            is_active=is_active,
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
