from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from fastapi.responses import RedirectResponse

from api.deps import OAuthService, get_oauth_service
from config.oauth import OAuthProvider
from config.settings import settings
from schemas.auth import UserType

router = APIRouter()


@router.get("/{provider}/callback/customer")
async def customer_oauth_callback(
    provider: OAuthProvider,
    response: Response,
    code: str = Query(...),
    state: str = Query(None, description="추후 보안을 위해 넣은 파라미터, 지금은 None으로 해도 상관없음"),
    oauth_service: OAuthService = Depends(get_oauth_service)
):
    """Customer OAuth 로그인 콜백"""
    try:
        token_response = await oauth_service.authenticate(
            provider=provider,
            code=code,
            user_type=UserType.CUSTOMER
        )
        
        # 프론트 로컬 개발 용
        if state == '1004':
            frontend_url = settings.FRONTEND_LOCAL_URL
        else:
            frontend_url = settings.FRONTEND_URL
            
        response = RedirectResponse(url=f"{frontend_url}/auth/success?token={token_response.access_token}")
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{provider}/callback/seller")
async def seller_oauth_callback(
    provider: OAuthProvider,
    response: Response,
    code: str = Query(...),
    state: str = Query(None, description="추후 보안을 위해 넣은 파라미터, 지금은 None으로 해도 상관없음"),
    oauth_service: OAuthService = Depends(get_oauth_service)
):
    """Seller OAuth 로그인 콜백"""
    try:
        token_response = await oauth_service.authenticate(
            provider=provider,
            code=code,
            user_type=UserType.SELLER
        )
        
        # 프론트 로컬 개발 용
        if state == '1004':
            frontend_url = settings.FRONTEND_LOCAL_URL
        else:
            frontend_url = settings.FRONTEND_URL
            
        response = RedirectResponse(url=f"{frontend_url}/auth/success?token={token_response.access_token}")
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )