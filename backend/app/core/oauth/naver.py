from app.core.oauth.base import OAuthClient, OAuthUser
from app.config.oauth import OAuthConfig, OAuthProvider


class NaverOAuthClient(OAuthClient):
    def __init__(self, config: OAuthConfig):
        super().__init__(config, OAuthProvider.NAVER)


    async def get_user_info(self, access_token: str) -> OAuthUser:
        response = await self.client.get(
            self.config.userinfo_url,
            headers={"Authorization": f"Bearer {access_token}"},
        )
        response.raise_for_status()

        user_data = response.json().get("response", {})
        # email 누락은 OAuthService 가 OAuthEmailMissingError 로 단일 분기한다.
        return OAuthUser(
            email=user_data.get("email") or "",
            provider=self.provider,
            name=user_data.get("name"),
        )
