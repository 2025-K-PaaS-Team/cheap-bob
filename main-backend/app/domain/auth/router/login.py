from fastapi.responses import RedirectResponse
from fastapi import APIRouter, Query

from app.domain.auth.service.oauth_state import DEV_LOCAL_STATE, OAuthStateService
from app.domain.auth.dto.auth import UserType
from app.core.oauth import create_oauth_client
from app.config.setting import settings
from app.config.oauth import OAuthProvider


router = APIRouter()


async def _resolve_state(provided_state: str | None, user_type: UserType) -> str:
    """OAuth state 결정.

    dev 환경의 매직값 (``DEV_LOCAL_STATE``) 은 그대로 통과 — frontend 로컬 분기 호환을
    위해 유지. 그 외엔 항상 서버가 UUID state 를 발급하고 Redis 에 저장 → callback 에서
    atomic 검증.
    """
    if provided_state == DEV_LOCAL_STATE and settings.ENVIRONMENT == "dev":
        return DEV_LOCAL_STATE
    return await OAuthStateService.issue(user_type)


@router.get("/{provider}/login/customer")
async def customer_oauth_login(
    provider: OAuthProvider,
    state: str = Query(
        None,
        description="dev local 분기 매직값 ('1004') 만 의미 있음. 그 외엔 무시되고 서버가 CSRF state 를 발급.",
    ),
):
    """Customer 의 OAuth 로그인 진입점. provider 의 authorize URL 로 302 리다이렉트.

    CSRF state 는 서버가 발급해 Redis 에 저장하고 (5분 TTL) provider 에 동봉한다.
    callback 에서 ``OAuthStateService.consume`` 으로 atomic GETDEL 검증.

    `async with` 는 client 리소스 라이프사이클을 명시한다. URL 생성만 하는 본 경로는
    lazy-init 덕분에 실제 `AsyncClient` 가 만들어지지 않는다.
    """
    effective_state = await _resolve_state(state, UserType.CUSTOMER)
    async with create_oauth_client(provider) as oauth_client:
        auth_url = oauth_client.get_authorization_url(
            state=effective_state,
            user_type=UserType.CUSTOMER.value,
        )
    return RedirectResponse(url=auth_url)


@router.get("/{provider}/login/seller")
async def seller_oauth_login(
    provider: OAuthProvider,
    state: str = Query(
        None,
        description="dev local 분기 매직값 ('1004') 만 의미 있음. 그 외엔 무시되고 서버가 CSRF state 를 발급.",
    ),
):
    """Seller 의 OAuth 로그인 진입점."""
    effective_state = await _resolve_state(state, UserType.SELLER)
    async with create_oauth_client(provider) as oauth_client:
        auth_url = oauth_client.get_authorization_url(
            state=effective_state,
            user_type=UserType.SELLER.value,
        )
    return RedirectResponse(url=auth_url)
