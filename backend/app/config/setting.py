from typing import Optional
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

    # 로깅
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "console"
    LOG_FILE_PATH: Optional[str] = None
    LOG_ROTATION: str = "100 MB"
    LOG_RETENTION: str = "30 days"
    LOG_COMPRESSION: str = "gz"
    
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
    
    # Oauth2.0 정보
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
    COOKIE_EXPIRE_SECONDS: int = 60 * 60 * 24 * 7  # 7 days (Set-Cookie max-age 단위)

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
    
    # MSA — service-to-service.
    # 양 서비스가 서로의 /api/internal/* 를 호출할 때 X-Internal-Token 헤더에 본 값을 실어 보낸다.
    INTERNAL_SERVICE_TOKEN: str
    # 본 backend 가 payment-svc 의 /api/internal/* 를 호출할 base URL.
    PAYMENT_SERVICE_URL: str

    # 슈퍼 어드민 이메일 정보 설정
    SUPER_ADMIN_SMTP_USER: str
    SUPER_ADMIN_SMTP_PASSWORD: str
    SUPER_ADMIN_SMTP_EMAIL: str
    SUPER_ADMIN_SMTP_HOST: str
    SUPER_ADMIN_SMTP_PORT: int
    SUPER_ADMIN_SMTP_NAME: str
    
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


    @property
    def is_production(self) -> bool:
        """LOG_FORMAT fail-safe 등 운영 환경 분기에 사용."""
        return self.ENVIRONMENT.lower() in {"prod", "production"}


settings = Settings()