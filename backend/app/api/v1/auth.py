from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import RedirectResponse

from app.api.deps import OAuthService, get_oauth_service
from app.config.oauth import OAuthProvider
from app.schemas.auth import TokenResponse, UserType
from app.services.oauth.factory import OAuthClientFactory

router = APIRouter(prefix="/auth", tags=["auth"])


# Customer OAuth 로그인
@router.get("/{provider}/login/customer")
async def customer_oauth_login(
    provider: OAuthProvider,
    state: str = Query(None)
):
    oauth_client = OAuthClientFactory.create(provider)
    auth_url = oauth_client.get_authorization_url(
        state=state or "",
        user_type=UserType.CUSTOMER.value
    )
    return RedirectResponse(url=auth_url)


@router.get("/{provider}/callback/customer", response_model=TokenResponse)
async def customer_oauth_callback(
    provider: OAuthProvider,
    code: str = Query(...),
    state: str = Query(None),
    oauth_service: OAuthService = Depends(get_oauth_service)
):
    try:
        return await oauth_service.authenticate(
            provider=provider,
            code=code,
            user_type=UserType.CUSTOMER
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# Seller OAuth 로그인
@router.get("/{provider}/login/seller")
async def seller_oauth_login(
    provider: OAuthProvider,
    state: str = Query(None)
):
    oauth_client = OAuthClientFactory.create(provider)
    auth_url = oauth_client.get_authorization_url(
        state=state or "",
        user_type=UserType.SELLER.value
    )
    return RedirectResponse(url=auth_url)


@router.get("/{provider}/callback/seller", response_model=TokenResponse)
async def seller_oauth_callback(
    provider: OAuthProvider,
    code: str = Query(...),
    state: str = Query(None),
    oauth_service: OAuthService = Depends(get_oauth_service)
):
    try:
        return await oauth_service.authenticate(
            provider=provider,
            code=code,
            user_type=UserType.SELLER
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )