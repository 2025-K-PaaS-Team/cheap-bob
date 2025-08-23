from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.repositories.customer import CustomerRepository
from app.repositories.seller import SellerRepository
from app.services.auth.jwt import JWTService
from app.services.auth.oauth_service import OAuthService


# Database dependency
AsyncSessionDep = Annotated[AsyncSession, Depends(get_db)]


# Repository dependencies
def get_customer_repository(session: AsyncSessionDep) -> CustomerRepository:
    return CustomerRepository(session)


def get_seller_repository(session: AsyncSessionDep) -> SellerRepository:
    return SellerRepository(session)


CustomerRepositoryDep = Annotated[CustomerRepository, Depends(get_customer_repository)]
SellerRepositoryDep = Annotated[SellerRepository, Depends(get_seller_repository)]


# Service dependencies
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