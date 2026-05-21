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
        email = user_data.get("email")
        if not email:
            raise ValueError("Email not provided by Naver")

        return OAuthUser(
            email=email,
            provider=self.provider,
            name=user_data.get("name"),
        )
