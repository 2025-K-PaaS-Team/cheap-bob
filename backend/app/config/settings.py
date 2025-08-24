from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )

    DEBUG: bool
    
    # Environment
    ENVIRONMENT: str
    FRONTEND_URL: str
    FRONTEND_LOCAL_URL: str
    
    # PostgreSQL 정보
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str
    
    #Oauth2.0 정보
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    KAKAO_CLIENT_ID: str
    KAKAO_CLIENT_SECRET: str
    NAVER_CLIENT_ID: str
    NAVER_CLIENT_SECRET: str
    
    # 암호화
    JWT_SECRET: str
    JWT_ALGORITHM: str
    JWT_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # OAuth Redirect URIs
    OAUTH_REDIRECT_BASE_URL: str

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    @property
    def SYNC_DATABASE_URL(self) -> str:
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


settings = Settings()