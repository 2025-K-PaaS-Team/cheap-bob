from urllib.parse import urlencode
from typing import Optional
from httpx import AsyncClient
from abc import ABC, abstractmethod

from app.config.oauth import OAuthConfig, OAuthProvider


class OAuthUser:
    """OAuth provider 가 응답한 사용자 식별 정보.

    email 은 본 시스템의 사용자 식별 키이므로 반드시 채워져야 한다.
    """

    def __init__(self, email: str, provider: OAuthProvider, name: Optional[str] = None):
        self.email = email
        self.provider = provider
        self.name = name


class OAuthClient(ABC):
    """OAuth provider 공통 동작 (authorize URL 생성, access token 교환).

    provider 별로 다른 user_info 응답 스키마는 `get_user_info` 에서 흡수한다.
    """

    def __init__(self, config: OAuthConfig, provider: OAuthProvider):
        self.config = config
        self.provider = provider
        self.client = AsyncClient()


    async def __aenter__(self):
        return self


    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()


    def get_authorization_url(self, state: str, user_type: str) -> str:
        params = {
            "client_id": self.config.client_id,
            "redirect_uri": f"{self.config.redirect_uri}/{user_type}",
            "response_type": "code",
            "state": state,
        }
        if self.config.scope:
            params["scope"] = self.config.scope

        # 한 디바이스에서 여러 계정을 쓰는 사용자가 직전 계정으로 자동 로그인되는
        # 사고를 막기 위해 provider 별로 계정 선택창을 강제한다.
        if self.provider == OAuthProvider.GOOGLE:
            params["prompt"] = "select_account"
        elif self.provider == OAuthProvider.KAKAO:
            params["prompt"] = "login"
        elif self.provider == OAuthProvider.NAVER:
            params["auth_type"] = "reauthenticate"

        return f"{self.config.authorize_url}?{urlencode(params)}"


    async def get_access_token(self, code: str, user_type: str) -> str:
        data = {
            "grant_type": "authorization_code",
            "client_id": self.config.client_id,
            "client_secret": self.config.client_secret,
            "redirect_uri": f"{self.config.redirect_uri}/{user_type}",
            "code": code,
        }

        response = await self.client.post(
            self.config.token_url,
            data=data,
            headers={"Accept": "application/json"},
        )
        response.raise_for_status()
        return response.json().get("access_token")


    @abstractmethod
    async def get_user_info(self, access_token: str) -> OAuthUser:
        ...
