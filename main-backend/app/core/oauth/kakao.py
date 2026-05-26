from app.core.oauth.base import OAuthClient, OAuthUser
from app.config.oauth import OAuthConfig, OAuthProvider


class KakaoOAuthClient(OAuthClient):
    def __init__(self, config: OAuthConfig):
        super().__init__(config, OAuthProvider.KAKAO)


    async def get_user_info(self, access_token: str) -> OAuthUser:
        response = await self.client.get(
            self.config.userinfo_url,
            headers={"Authorization": f"Bearer {access_token}"},
        )
        response.raise_for_status()

        user_data = response.json()
        kakao_account = user_data.get("kakao_account", {})
        name = kakao_account.get("profile", {}).get("nickname")
        # email 누락은 OAuthService 가 OAuthEmailMissingError 로 단일 분기한다.
        return OAuthUser(
            email=kakao_account.get("email") or "",
            provider=self.provider,
            name=name,
        )
