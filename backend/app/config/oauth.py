from dataclasses import dataclass
from enum import Enum
from typing import Dict

from app.config.settings import settings


class OAuthProvider(str, Enum):
    GOOGLE = "google"
    KAKAO = "kakao"
    NAVER = "naver"


@dataclass
class OAuthConfig:
    client_id: str
    client_secret: str
    authorize_url: str
    token_url: str
    userinfo_url: str
    redirect_uri: str
    scope: str


OAUTH_CONFIGS: Dict[OAuthProvider, OAuthConfig] = {
    OAuthProvider.GOOGLE: OAuthConfig(
        client_id=settings.GOOGLE_CLIENT_ID,
        client_secret=settings.GOOGLE_CLIENT_SECRET,
        authorize_url="https://accounts.google.com/o/oauth2/v2/auth",
        token_url="https://oauth2.googleapis.com/token",
        userinfo_url="https://www.googleapis.com/oauth2/v2/userinfo",
        redirect_uri=f"{settings.OAUTH_REDIRECT_BASE_URL}/api/v1/auth/google/callback",
        scope="openid email profile"
    ),
    OAuthProvider.KAKAO: OAuthConfig(
        client_id=settings.KAKAO_CLIENT_ID,
        client_secret=settings.KAKAO_CLIENT_SECRET,
        authorize_url="https://kauth.kakao.com/oauth/authorize",
        token_url="https://kauth.kakao.com/oauth/token",
        userinfo_url="https://kapi.kakao.com/v2/user/me",
        redirect_uri=f"{settings.OAUTH_REDIRECT_BASE_URL}/api/v1/auth/kakao/callback",
        scope=""
    ),
    OAuthProvider.NAVER: OAuthConfig(
        client_id=settings.NAVER_CLIENT_ID,
        client_secret=settings.NAVER_CLIENT_SECRET,
        authorize_url="https://nid.naver.com/oauth2.0/authorize",
        token_url="https://nid.naver.com/oauth2.0/token",
        userinfo_url="https://openapi.naver.com/v1/nid/me",
        redirect_uri=f"{settings.OAUTH_REDIRECT_BASE_URL}/api/v1/auth/naver/callback",
        scope=""
    )
}