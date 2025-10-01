from typing import Union, Tuple

from fastapi import HTTPException, status

from config.oauth import OAuthProvider
from repositories.customer import CustomerRepository
from repositories.seller import SellerRepository
from schemas.auth import TokenResponse, UserType
from services.auth.jwt import JWTService
from services.oauth.factory import OAuthClientFactory


class OAuthService:
    def __init__(
        self,
        customer_repository: CustomerRepository,
        seller_repository: SellerRepository,
        jwt_service: JWTService
    ):
        self.customer_repository = customer_repository
        self.seller_repository = seller_repository
        self.jwt_service = jwt_service
    
    async def authenticate(
        self, 
        provider: OAuthProvider,
        code: str,
        user_type: UserType
    ) -> TokenResponse:
        # OAuth 클라이언트 생성
        oauth_client = OAuthClientFactory.create(provider)
        
        async with oauth_client:
            # 액세스 토큰 획득
            access_token = await oauth_client.get_access_token(code, user_type.value)
            
            # 사용자 정보 획득
            oauth_user = await oauth_client.get_user_info(access_token)
        
        # 사용자 타입에 따라 처리
        if user_type == UserType.CUSTOMER:
            return await self._handle_customer_login(oauth_user.email)
        else:
            return await self._handle_seller_login(oauth_user.email)
    
    async def _handle_customer_login(self, email: str) -> Tuple[TokenResponse, bool]:
        # Seller로 이미 가입되어 있는지 체크
        seller_exists = await self.seller_repository.exists_by_email(email)
        if seller_exists:
            # 이미 판매자로 가입, 충돌 발생
            access_token = self.jwt_service.create_user_token(
                email=email,
                user_type=UserType.SELLER.value
            )
            return TokenResponse(access_token=access_token, user_type=UserType.SELLER), True
            # raise HTTPException(
            #     status_code=status.HTTP_409_CONFLICT,
            #     detail="이미 판매자로 존재하는 회원입니다."
            # )
        
        # Customer로 가입되어 있는지 체크
        customer_exists = await self.customer_repository.exists_by_email(email)
        
        if not customer_exists:
            # 신규 회원 생성
            await self.customer_repository.create(email=email)
        
        # JWT 토큰 생성
        access_token = self.jwt_service.create_user_token(
            email=email,
            user_type=UserType.CUSTOMER.value
        )
        
        return TokenResponse(access_token=access_token, user_type=UserType.CUSTOMER), False
    
    async def _handle_seller_login(self, email: str) -> Tuple[TokenResponse, bool]:
        # Customer로 이미 가입되어 있는지 체크
        customer_exists = await self.customer_repository.exists_by_email(email)
        if customer_exists:
            # 이미 소비자로 가입, 충돌 발생
            access_token = self.jwt_service.create_user_token(
                email=email,
                user_type=UserType.CUSTOMER.value
            )
            return TokenResponse(access_token=access_token, user_type=UserType.CUSTOMER), True
            # raise HTTPException(
            #     status_code=status.HTTP_409_CONFLICT,
            #     detail="이미 소비자로 존재하는 회원입니다."
            # )
        
        # Seller로 가입되어 있는지 체크
        seller_exists = await self.seller_repository.exists_by_email(email)
        
        if not seller_exists:
            # 신규 회원 생성
            await self.seller_repository.create(email=email)
        
        # JWT 토큰 생성
        access_token = self.jwt_service.create_user_token(
            email=email,
            user_type=UserType.SELLER.value
        )
        
        return TokenResponse(access_token=access_token,user_type=UserType.SELLER), False