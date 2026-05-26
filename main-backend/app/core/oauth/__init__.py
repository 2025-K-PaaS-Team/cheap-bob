from typing import Dict, Type

from app.core.oauth.naver import NaverOAuthClient
from app.core.oauth.kakao import KakaoOAuthClient
from app.core.oauth.google import GoogleOAuthClient
from app.core.oauth.base import OAuthClient, OAuthUser
from app.config.oauth import OAUTH_CONFIGS, OAuthProvider


# provider 추가 시 본 dict 와 `app/config/oauth.py` 의 `OAUTH_CONFIGS` 를 동시에 갱신한다.
# 한쪽만 갱신하면 dispatch 가 KeyError 로 죽거나, config 가 있는데 client 가 없어 실패한다.
OAUTH_CLIENTS: Dict[OAuthProvider, Type[OAuthClient]] = {
    OAuthProvider.GOOGLE: GoogleOAuthClient,
    OAuthProvider.KAKAO: KakaoOAuthClient,
    OAuthProvider.NAVER: NaverOAuthClient,
}


def create_oauth_client(provider: OAuthProvider) -> OAuthClient:
    """provider 에 매핑된 OAuthClient 인스턴스를 생성한다."""
    config = OAUTH_CONFIGS.get(provider)
    if config is None:
        raise ValueError(f"Unknown OAuth provider: {provider}")
    client_cls = OAUTH_CLIENTS.get(provider)
    if client_cls is None:
        raise ValueError(f"Unsupported OAuth provider: {provider}")
    return client_cls(config)


__all__ = ["OAuthClient", "OAuthUser", "OAUTH_CLIENTS", "create_oauth_client"]
