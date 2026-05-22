from fastapi.responses import RedirectResponse
from fastapi import APIRouter, Depends, Query
from dependency_injector.wiring import Provide, inject

from app.domain.auth.service.registration_status import RegistrationStatusService
from app.domain.auth.service.oauth_state import DEV_LOCAL_STATE, OAuthStateService
from app.domain.auth.service.oauth import OAuthService
from app.domain.auth.service.exception import OAuthAuthenticationError
from app.domain.auth.dto.auth import UserType
from app.domain.auth.service.cookie import set_auth_cookie
from app.config.setting import settings
from app.config.oauth import OAuthProvider


router = APIRouter()


async def _verify_state(state: str | None, *, expected_type: UserType) -> bool:
    """CSRF state 검증. dev 환경 매직값만 우회 — 그 외엔 Redis atomic GETDEL.

    Returns True 면 통과, False 면 거부 (callback 라우터가 error redirect).
    """
    if state == DEV_LOCAL_STATE and settings.ENVIRONMENT == "dev":
        return True
    return await OAuthStateService.consume(state, expected_type=expected_type)


def _frontend_base(*, is_local_dev: bool) -> str:
    return settings.FRONTEND_LOCAL_URL if is_local_dev else settings.FRONTEND_URL


def _build_success_redirect(
    *,
    is_local_dev: bool,
    registration_status: str,
    conflict: bool,
    access_token: str,
) -> RedirectResponse:
    """프론트 success 페이지로 redirect + httpOnly 쿠키.

    쿠키 정책 (SameSite / max_age / Secure) 은 `auth/cookie.py` 의 helper 가 단일 관리한다.
    """
    response = RedirectResponse(
        url=(
            f"{_frontend_base(is_local_dev=is_local_dev)}"
            f"/auth/success?status={registration_status}&conflict={int(conflict)}"
        ),
    )
    set_auth_cookie(response, access_token)
    return response


def _build_error_redirect(*, is_local_dev: bool, reason: str) -> RedirectResponse:
    """프론트 error 페이지로 redirect. 쿠키는 발급하지 않는다.

    `reason` 은 `OAuthAuthenticationError.reason` 에서 온다 (예: oauth_failed, email_missing).
    """
    return RedirectResponse(
        url=f"{_frontend_base(is_local_dev=is_local_dev)}/auth/error?reason={reason}",
    )


@router.get("/{provider}/callback/customer")
@inject
async def customer_oauth_callback(
    provider: OAuthProvider,
    code: str = Query(...),
    state: str = Query(None, description="login 시 발급된 CSRF state — Redis 에서 atomic 검증."),
    oauth_service: OAuthService = Depends(Provide["oauth_service"]),
    registration_status_service: RegistrationStatusService = Depends(
        Provide["registration_status_service"],
    ),
):
    """Customer 진입의 OAuth 콜백.

    0) state CSRF 검증 (Redis atomic GETDEL — 재사용 불가)
    1) provider code 교환 + 가입/조회 + JWT 발급
    2) 충돌(반대 타입) 여부에 따라 등록 단계 판별 대상 결정
    3) 성공: success 페이지로 302 + httpOnly 쿠키. OAuth 실패: error 페이지로 302.
       DB / 내부 오류는 catch 하지 않고 글로벌 핸들러 (5xx) 로 보낸다 — 알람/모니터링이 정상 동작해야 한다.
    """
    is_local_dev = state == DEV_LOCAL_STATE and settings.ENVIRONMENT == "dev"

    if not await _verify_state(state, expected_type=UserType.CUSTOMER):
        return _build_error_redirect(
            is_local_dev=is_local_dev, reason="csrf_state_mismatch",
        )

    try:
        result = await oauth_service.authenticate(
            provider=provider,
            code=code,
            requested_type=UserType.CUSTOMER,
        )
    except OAuthAuthenticationError as e:
        return _build_error_redirect(is_local_dev=is_local_dev, reason=e.reason)

    registration_status = await registration_status_service.get_status(
        email=result.email,
        user_type=result.user_type,
    )

    return _build_success_redirect(
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
    state: str = Query(None, description="login 시 발급된 CSRF state — Redis 에서 atomic 검증."),
    oauth_service: OAuthService = Depends(Provide["oauth_service"]),
    registration_status_service: RegistrationStatusService = Depends(
        Provide["registration_status_service"],
    ),
):
    """Seller 진입의 OAuth 콜백."""
    is_local_dev = state == DEV_LOCAL_STATE and settings.ENVIRONMENT == "dev"

    if not await _verify_state(state, expected_type=UserType.SELLER):
        return _build_error_redirect(
            is_local_dev=is_local_dev, reason="csrf_state_mismatch",
        )

    try:
        result = await oauth_service.authenticate(
            provider=provider,
            code=code,
            requested_type=UserType.SELLER,
        )
    except OAuthAuthenticationError as e:
        return _build_error_redirect(is_local_dev=is_local_dev, reason=e.reason)

    registration_status = await registration_status_service.get_status(
        email=result.email,
        user_type=result.user_type,
    )

    return _build_success_redirect(
        is_local_dev=is_local_dev,
        registration_status=registration_status,
        conflict=result.conflict,
        access_token=result.access_token,
    )
