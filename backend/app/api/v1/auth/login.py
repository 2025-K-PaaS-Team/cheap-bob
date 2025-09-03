from fastapi import APIRouter, Query
from fastapi.responses import RedirectResponse

from config.oauth import OAuthProvider
from schemas.auth import UserType
from services.oauth.factory import OAuthClientFactory

router = APIRouter()


@router.get("/{provider}/login/customer")
async def customer_oauth_login(
    provider: OAuthProvider,
    state: str = Query(None, description="추후 보안을 위해 넣은 파라미터, 지금은 None으로 해도 상관없음")
):
    """Customer OAuth 로그인"""
    oauth_client = OAuthClientFactory.create(provider)
    
    auth_url = oauth_client.get_authorization_url(
        state=state or "",
        user_type=UserType.CUSTOMER.value
    )
    return RedirectResponse(url=auth_url)


@router.get("/{provider}/login/seller")
async def seller_oauth_login(
    provider: OAuthProvider,
    state: str = Query(None, description="추후 보안을 위해 넣은 파라미터, 지금은 None으로 해도 상관없음")
):
    """Seller OAuth 로그인"""
    oauth_client = OAuthClientFactory.create(provider)
    
    auth_url = oauth_client.get_authorization_url(
        state=state or "",
        user_type=UserType.SELLER.value
    )
    
    return RedirectResponse(url=auth_url)