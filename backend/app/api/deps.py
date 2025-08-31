from typing import Annotated, Dict

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from database.session import get_db
from repositories.customer import CustomerRepository
from repositories.seller import SellerRepository
from services.auth.jwt import JWTService
from services.auth.oauth_service import OAuthService


# ==================== Database Dependencies ====================
AsyncSessionDep = Annotated[AsyncSession, Depends(get_db)]


# ==================== Repository Dependencies ====================
def get_customer_repository(session: AsyncSessionDep) -> CustomerRepository:
    return CustomerRepository(session)


def get_seller_repository(session: AsyncSessionDep) -> SellerRepository:
    return SellerRepository(session)


CustomerRepositoryDep = Annotated[CustomerRepository, Depends(get_customer_repository)]
SellerRepositoryDep = Annotated[SellerRepository, Depends(get_seller_repository)]


# ==================== Service Dependencies ====================
def get_jwt_service() -> JWTService:
    return JWTService()


def get_oauth_service(
    customer_repository: CustomerRepositoryDep,
    seller_repository: SellerRepositoryDep,
    jwt_service: Annotated[JWTService, Depends(get_jwt_service)]
) -> OAuthService:
    return OAuthService(
        customer_repository=customer_repository,
        seller_repository=seller_repository,
        jwt_service=jwt_service
    )


# ==================== Auth Dependencies ====================
class AuthenticationError(HTTPException):
    def __init__(self, detail: str = "인증이 필요합니다"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


class PermissionError(HTTPException):
    def __init__(self, detail: str = "권한이 없습니다"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail
        )


async def get_current_user(request: Request) -> Dict:
    """현재 인증된 사용자 정보를 반환합니다."""
    if not hasattr(request.state, 'user'):
        raise AuthenticationError()
    return request.state.user


async def get_current_customer(
    current_user: Annotated[Dict, Depends(get_current_user)]
) -> Dict:
    """Customer 권한을 가진 사용자만 접근 가능"""
    if current_user.get("user_type") != "customer":
        raise PermissionError("Customer 권한이 필요합니다")
    return current_user


async def get_current_seller(
    current_user: Annotated[Dict, Depends(get_current_user)]
) -> Dict:
    """Seller 권한을 가진 사용자만 접근 가능"""
    if current_user.get("user_type") != "seller":
        raise PermissionError("Seller 권한이 필요합니다")
    return current_user


async def get_current_user_optional(request: Request) -> Dict | None:
    """선택적 인증 - 인증이 없어도 접근 가능하지만, 인증된 경우 사용자 정보 반환"""
    if hasattr(request.state, 'user'):
        return request.state.user
    return None


# ==================== Type Aliases for Dependency Injection ====================
CurrentUserDep = Annotated[Dict, Depends(get_current_user)]
CurrentCustomerDep = Annotated[Dict, Depends(get_current_customer)]
CurrentSellerDep = Annotated[Dict, Depends(get_current_seller)]
CurrentUserOptionalDep = Annotated[Dict | None, Depends(get_current_user_optional)]
OAuthServiceDep = Annotated[OAuthService, Depends(get_oauth_service)]
JWTServiceDep = Annotated[JWTService, Depends(get_jwt_service)]