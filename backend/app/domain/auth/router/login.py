from fastapi.responses import RedirectResponse
from fastapi import APIRouter, Query

from app.domain.auth.dto.auth import UserType
from app.core.oauth import create_oauth_client
from app.config.oauth import OAuthProvider


router = APIRouter()


@router.get("/{provider}/login/customer")
async def customer_oauth_login(
    provider: OAuthProvider,
    state: str = Query(None, description="추후 보안용 파라미터. 현재는 None 허용."),
):
    """Customer 의 OAuth 로그인 진입점. provider 의 authorize URL 로 302 리다이렉트.

    `async with` 는 client 리소스 라이프사이클을 명시한다. URL 생성만 하는 본 경로는
    lazy-init 덕분에 실제 `AsyncClient` 가 만들어지지 않는다.
    """
    async with create_oauth_client(provider) as oauth_client:
        auth_url = oauth_client.get_authorization_url(
            state=state or "",
            user_type=UserType.CUSTOMER.value,
        )
    return RedirectResponse(url=auth_url)


@router.get("/{provider}/login/seller")
async def seller_oauth_login(
    provider: OAuthProvider,
    state: str = Query(None, description="추후 보안용 파라미터. 현재는 None 허용."),
):
    """Seller 의 OAuth 로그인 진입점."""
    async with create_oauth_client(provider) as oauth_client:
        auth_url = oauth_client.get_authorization_url(
            state=state or "",
            user_type=UserType.SELLER.value,
        )
    return RedirectResponse(url=auth_url)
