from fastapi import APIRouter, HTTPException, Query, Response, status
from fastapi.responses import RedirectResponse

from utils.docs_error import create_error_responses

from api.deps.service import (
    OAuthServiceDep,
    JWTServiceDep
)
from api.deps.repository import StoreRepositoryDep, StoreProductInfoRepositoryDep, CustomerDetailRepositoryDep

from config.oauth import OAuthProvider
from config.settings import settings
from schemas.auth import UserType
from utils.user_utils import get_customer_status, get_seller_status

router = APIRouter()

@router.get("/{provider}/callback/customer",
    responses=create_error_responses({         
        400:"Oauth 로그인 에러가 발생"
    })   
)
async def customer_oauth_callback(
    provider: OAuthProvider,
    response: Response,
    customer_detail_repo: CustomerDetailRepositoryDep,
    store_repo: StoreRepositoryDep,
    product_repo: StoreProductInfoRepositoryDep,
    oauth_service: OAuthServiceDep,
    jwt_service: JWTServiceDep,
    code: str = Query(...),
    state: str = Query(None, description="추후 보안을 위해 넣은 파라미터, 지금은 None으로 해도 상관없음")
):
    """Customer OAuth 로그인 콜백"""
    try:
        token_response, conflict = await oauth_service.authenticate(
            provider=provider,
            code=code,
            user_type=UserType.CUSTOMER
        )
        
        decoded_token = jwt_service.decode_access_token(token_response.access_token)
        email = decoded_token["sub"]
        
        if conflict:
            registration_status = await get_seller_register(email, store_repo, product_repo)
        else:
            registration_status = await get_customer_register(email,customer_detail_repo)
        
        # 프론트 로컬 개발 용
        if state == '1004' and settings.ENVIRONMENT == "dev":
            response = RedirectResponse(
                url=f"{settings.FRONTEND_LOCAL_URL}/auth/success?&status={registration_status}&conflict={int(conflict)}"
            )
            response.set_cookie(
                key="access_token",
                value=token_response.access_token,
                httponly=True,
                secure=True,
                samesite="none",
                max_age=settings.COOKIE_EXPIRE_MINUTES,
                path="/"
            )
            
        else:
            response = RedirectResponse(
                url=f"{settings.FRONTEND_URL}/auth/success?status={registration_status}&conflict={int(conflict)}"
            )
            response.set_cookie(
                key="access_token",
                value=token_response.access_token,
                httponly=True,
                secure=True,
                samesite="lax",
                max_age=settings.COOKIE_EXPIRE_MINUTES,
                path="/"
            )
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{provider}/callback/seller",
    responses=create_error_responses({         
        400:"Oauth 로그인 에러가 발생"
    })
)
async def seller_oauth_callback(
    provider: OAuthProvider,
    response: Response,
    customer_detail_repo: CustomerDetailRepositoryDep,
    store_repo: StoreRepositoryDep,
    product_repo: StoreProductInfoRepositoryDep,
    oauth_service: OAuthServiceDep,
    jwt_service: JWTServiceDep,
    code: str = Query(...),
    state: str = Query(None, description="추후 보안을 위해 넣은 파라미터, 지금은 None으로 해도 상관없음")
):
    """Seller OAuth 로그인 콜백"""
    try:
        token_response, conflict = await oauth_service.authenticate(
            provider=provider,
            code=code,
            user_type=UserType.SELLER
        )
        
        # JWT 토큰을 디코드하여 판매자 이메일 추출
        decoded_token = jwt_service.decode_access_token(token_response.access_token)
        email = decoded_token["sub"]
        
        if conflict:
            registration_status = await get_customer_register(email,customer_detail_repo)
        else:
            registration_status = await get_seller_register(email, store_repo, product_repo)
        
        # 프론트 로컬 개발 용
        if state == '1004' and settings.ENVIRONMENT == "dev":
            response = RedirectResponse(
                url=f"{settings.FRONTEND_LOCAL_URL}/auth/success?&status={registration_status}&conflict={int(conflict)}"
            )
            response.set_cookie(
                key="access_token",
                value=token_response.access_token,
                httponly=True,
                secure=True,
                samesite="none",
                max_age=settings.COOKIE_EXPIRE_MINUTES,
                path="/"
            )
            
        else:
            response = RedirectResponse(
                url=f"{settings.FRONTEND_URL}/auth/success?status={registration_status}&conflict={int(conflict)}"
            )
            response.set_cookie(
                key="access_token",
                value=token_response.access_token,
                httponly=True,
                secure=True,
                samesite="lax",
                max_age=settings.COOKIE_EXPIRE_MINUTES,
                path="/"
            )
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )