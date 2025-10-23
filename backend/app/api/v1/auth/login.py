from fastapi import APIRouter, Query
from fastapi.responses import RedirectResponse, JSONResponse

from config.oauth import OAuthProvider
from schemas.auth import UserType
from services.oauth.factory import OAuthClientFactory
from config.settings import settings

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


@router.post("/logout")
async def logout(state: str = Query(None, description="로컬 테스트 용")):
    """로그아웃 - 쿠키 삭제"""
    response = JSONResponse(
        content={"message": "로그아웃되었습니다."},
        status_code=200
    )
    if state == "1004" and settings.ENVIRONMENT == "dev":
        response.set_cookie(
            key="access_token",
            value="",
            httponly=True,
            secure=True,
            samesite="none",
            max_age=0,
            path="/"
        )
        
    else:
        response.set_cookie(
            key="access_token",
            value="",
            httponly=True,
            secure=True,
            samesite="lax",
            max_age=0,
            path="/"
        )
    
    return response