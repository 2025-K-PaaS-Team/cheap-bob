from config.oauth import OAUTH_CONFIGS, OAuthProvider
from services.oauth.base import OAuthClient
from services.oauth.google import GoogleOAuthClient
from services.oauth.kakao import KakaoOAuthClient
from services.oauth.naver import NaverOAuthClient


class OAuthClientFactory:
    @staticmethod
    def create(provider: OAuthProvider) -> OAuthClient:
        config = OAUTH_CONFIGS.get(provider)
        if not config:
            raise ValueError(f"Unknown OAuth provider: {provider}")
        
        if provider == OAuthProvider.GOOGLE:
            return GoogleOAuthClient(config)
        elif provider == OAuthProvider.KAKAO:
            return KakaoOAuthClient(config)
        elif provider == OAuthProvider.NAVER:
            return NaverOAuthClient(config)
        else:
            raise ValueError(f"Unsupported OAuth provider: {provider}")