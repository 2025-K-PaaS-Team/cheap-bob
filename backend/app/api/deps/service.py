from typing import Annotated

from fastapi import Depends

from api.deps.database import AsyncSessionDep
from services.auth.jwt import JWTService
from services.auth.oauth_service import OAuthService
from services.image import ImageService


def get_jwt_service() -> JWTService:
    return JWTService()


def get_oauth_service(
    session: AsyncSessionDep,
    jwt_service: Annotated[JWTService, Depends(get_jwt_service)]
) -> OAuthService:
    from repositories.customer import CustomerRepository
    from repositories.seller import SellerRepository
    return OAuthService(
        customer_repository=CustomerRepository(session),
        seller_repository=SellerRepository(session),
        jwt_service=jwt_service
    )


def get_image_service(session: AsyncSessionDep) -> ImageService:
    return ImageService(session)


JWTServiceDep = Annotated[JWTService, Depends(get_jwt_service)]
OAuthServiceDep = Annotated[OAuthService, Depends(get_oauth_service)]
ImageServiceDep = Annotated[ImageService, Depends(get_image_service)]