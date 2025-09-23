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
    
    # Redis 정보
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_DB: int
    
    # MongoDB 정보
    MONGODB_HOST: str
    MONGODB_PORT: int
    MONGODB_USER: str
    MONGODB_PASSWORD: str
    MONGODB_NAME: str
    
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
    
    # 낙관적 Lock 재시도 횟수
    MAX_RETRY_LOCK: int
    
    # AWS S3 설정
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_REGION: str
    AWS_S3_BUCKET_NAME: str
    AWS_S3_ENDPOINT_URL: str
    
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    @property
    def SYNC_DATABASE_URL(self) -> str:
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    @property
    def REDIS_URL(self) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
    
    @property
    def MONGODB_URL(self) -> str:
        return f"mongodb://{self.MONGODB_USER}:{self.MONGODB_PASSWORD}@{self.MONGODB_HOST}:{self.MONGODB_PORT}/{self.MONGODB_NAME}?authSource=admin"


settings = Settings()