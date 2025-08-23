from app.config.oauth import OAuthConfig, OAuthProvider
from app.services.oauth.base import OAuthClient, OAuthUser


class KakaoOAuthClient(OAuthClient):
    def __init__(self, config: OAuthConfig):
        super().__init__(config, OAuthProvider.KAKAO)
    
    async def get_user_info(self, access_token: str) -> OAuthUser:
        response = await self.client.get(
            self.config.userinfo_url,
            headers={"Authorization": f"Bearer {access_token}"}
        )
        response.raise_for_status()
        
        user_data = response.json()
        kakao_account = user_data.get("kakao_account", {})
        
        email = kakao_account.get("email")
        if not email:
            raise ValueError("Email not provided by Kakao")
        
        profile = kakao_account.get("profile", {})
        name = profile.get("nickname")
        
        return OAuthUser(
            email=email,
            provider=self.provider,
            name=name
        )