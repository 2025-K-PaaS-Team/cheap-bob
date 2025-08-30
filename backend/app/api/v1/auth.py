from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status
from fastapi.responses import RedirectResponse

from api.deps import OAuthService, get_jwt_service, get_oauth_service
from config.oauth import OAuthProvider
from config.settings import settings
from schemas.auth import TokenResponse, UserType
from services.auth.jwt import JWTService
from services.oauth.factory import OAuthClientFactory

router = APIRouter(prefix="/auth", tags=["auth"])


# Customer OAuth 로그인
@router.get("/{provider}/login/customer")
async def customer_oauth_login(
    provider: OAuthProvider,
    state: str = Query(None, description= "추후 보안을 위해 넣은 파라미터, 지금은 None으로 해도 상관없음")
):
    # oauth 로그인 선택
    oauth_client = OAuthClientFactory.create(provider)
    
    # oauth Redirect
    auth_url = oauth_client.get_authorization_url(
        state=state or "",
        user_type=UserType.CUSTOMER.value
    )
    return RedirectResponse(url=auth_url)


# Customer OAuth 로그인 콜백
@router.get("/{provider}/callback/customer")
async def customer_oauth_callback(
    provider: OAuthProvider,
    response: Response,
    code: str = Query(...),
    state: str = Query(None, description= "추후 보안을 위해 넣은 파라미터, 지금은 None으로 해도 상관없음"),
    oauth_service: OAuthService = Depends(get_oauth_service)
):
    try:
        # 토큰 생성
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


# Seller OAuth 로그인
@router.get("/{provider}/login/seller")
async def seller_oauth_login(
    provider: OAuthProvider,
    state: str = Query(None, description= "추후 보안을 위해 넣은 파라미터, 지금은 None으로 해도 상관없음")
):
    # oauth 로그인 선택
    oauth_client = OAuthClientFactory.create(provider)
    
    # oauth Redirect
    auth_url = oauth_client.get_authorization_url(
        state=state or "",
        user_type=UserType.SELLER.value
    )
    
    return RedirectResponse(url=auth_url)


# Seller OAuth 로그인 콜백
@router.get("/{provider}/callback/seller")
async def seller_oauth_callback(
    provider: OAuthProvider,
    response: Response,
    code: str = Query(...),
    state: str = Query(None, description= "추후 보안을 위해 넣은 파라미터, 지금은 None으로 해도 상관없음"),
    oauth_service: OAuthService = Depends(get_oauth_service)
):
    try:
        # 토큰 생성
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


# 토큰 갱신 엔드포인트
@router.post("/refresh")
async def refresh_token(
    request: Request,
    jwt_service: JWTService = Depends(get_jwt_service)
):
    """JWT 토큰을 갱신하는 엔드포인트"""
    # Authorization 헤더에서 토큰 추출
    authorization = request.headers.get("Authorization")
    
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 인증 헤더입니다."
        )
    
    token = authorization[7:]  # "Bearer " 제거
    
    # 토큰 검증 및 갱신
    is_valid, new_token, payload = jwt_service.verify_and_refresh_token(token)
    
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 토큰입니다."
        )
    
    # 새 토큰이 생성되었으면 반환, 아니면 기존 토큰 반환
    return TokenResponse(
        access_token=new_token if new_token else token
    )