from typing import Annotated

from fastapi import Depends

from api.deps.repository import CustomerRepositoryDep, SellerRepositoryDep
from api.deps.database import AsyncSessionDep
from services.auth.jwt import JWTService
from services.auth.oauth_service import OAuthService
from services.image import ImageService


def get_jwt_service() -> JWTService:
    return JWTService()


def get_oauth_service(
    jwt_service: Annotated[JWTService, Depends(get_jwt_service)]
) -> OAuthService:
    return OAuthService(
        customer_repository=CustomerRepositoryDep,
        seller_repository=SellerRepositoryDep,
        jwt_service=jwt_service
    )


def get_image_service(session: AsyncSessionDep) -> ImageService:
    return ImageService(session)


JWTServiceDep = Annotated[JWTService, Depends(get_jwt_service)]
OAuthServiceDep = Annotated[OAuthService, Depends(get_oauth_service)]
ImageServiceDep = Annotated[ImageService, Depends(get_image_service)]