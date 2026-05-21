from fastapi.responses import RedirectResponse
from fastapi import APIRouter, Depends, HTTPException, Query, status
from dependency_injector.wiring import Provide, inject

from app.domain.auth.service.registration_status import RegistrationStatusService
from app.domain.auth.service.oauth import OAuthService
from app.domain.auth.dto.auth import UserType
from app.config.setting import settings
from app.config.oauth import OAuthProvider


router = APIRouter()


def _build_redirect(
    *,
    is_local_dev: bool,
    registration_status: str,
    conflict: bool,
    access_token: str,
) -> RedirectResponse:
    """프론트 redirect URL + access_token 쿠키 설정.

    dev 의 localhost 흐름은 SameSite=None (cross-site 쿠키 첨부) 이 필요하지만
    prod 는 SameSite=lax 로 CSRF 위험을 줄인다.
    """
    base = settings.FRONTEND_LOCAL_URL if is_local_dev else settings.FRONTEND_URL
    response = RedirectResponse(
        url=f"{base}/auth/success?status={registration_status}&conflict={int(conflict)}",
    )
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=True,
        samesite="none" if is_local_dev else "lax",
        max_age=settings.COOKIE_EXPIRE_MINUTES,
        path="/",
    )
    return response


@router.get("/{provider}/callback/customer")
@inject
async def customer_oauth_callback(
    provider: OAuthProvider,
    code: str = Query(...),
    state: str = Query(None, description="dev local 분기용 (1004) — 추후 CSRF state 토큰 자리."),
    oauth_service: OAuthService = Depends(Provide["oauth_service"]),
    registration_status_service: RegistrationStatusService = Depends(
        Provide["registration_status_service"],
    ),
):
    """Customer 진입의 OAuth 콜백.

    1) provider code 교환 + 가입/조회 + JWT 발급
    2) 충돌(반대 타입) 여부에 따라 등록 단계 판별 대상 결정
    3) 프론트 success 페이지로 302 + httpOnly access_token 쿠키
    """
    try:
        result = await oauth_service.authenticate(
            provider=provider,
            code=code,
            requested_type=UserType.CUSTOMER,
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    registration_status = await registration_status_service.get_status(
        email=result.email,
        user_type=result.user_type,
    )

    is_local_dev = state == "1004" and settings.ENVIRONMENT == "dev"
    return _build_redirect(
        is_local_dev=is_local_dev,
        registration_status=registration_status,
        conflict=result.conflict,
        access_token=result.access_token,
    )


@router.get("/{provider}/callback/seller")
@inject
async def seller_oauth_callback(
    provider: OAuthProvider,
    code: str = Query(...),
    state: str = Query(None, description="dev local 분기용 (1004)"),
    oauth_service: OAuthService = Depends(Provide["oauth_service"]),
    registration_status_service: RegistrationStatusService = Depends(
        Provide["registration_status_service"],
    ),
):
    """Seller 진입의 OAuth 콜백."""
    try:
        result = await oauth_service.authenticate(
            provider=provider,
            code=code,
            requested_type=UserType.SELLER,
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    registration_status = await registration_status_service.get_status(
        email=result.email,
        user_type=result.user_type,
    )

    is_local_dev = state == "1004" and settings.ENVIRONMENT == "dev"
    return _build_redirect(
        is_local_dev=is_local_dev,
        registration_status=registration_status,
        conflict=result.conflict,
        access_token=result.access_token,
    )
