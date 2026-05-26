from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """payment-backend 의 환경 설정. main-backend 와 별도 DB / 별도 .env 지만 JWT_SECRET
    등 일부는 환경변수로 공유한다.
    """
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

    DEBUG: bool

    ENVIRONMENT: str
    FRONTEND_URL: str
    FRONTEND_LOCAL_URL: str

    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "console"
    LOG_FILE_PATH: Optional[str] = None
    LOG_ROTATION: str = "100 MB"
    LOG_RETENTION: str = "30 days"
    LOG_COMPRESSION: str = "gz"

    # PostgreSQL — payment-backend 전용 DB.
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str

    # 암호화 — main-backend 와 동일 JWT_SECRET 을 공유 (양쪽 다 cookie 를 직접 검증).
    JWT_SECRET: str
    JWT_ALGORITHM: str
    JWT_EXPIRE_MINUTES: int = 60 * 24 * 7
    COOKIE_EXPIRE_SECONDS: int = 60 * 60 * 24 * 7

    MAX_RETRY_LOCK: int = 3

    # MSA — service-to-service.
    # main-backend 와 동일 토큰을 양쪽에 주입한다. 양 서비스가 서로의 /api/internal/* 를 호출할 때
    # X-Internal-Token 헤더에 본 값을 실어 보낸다.
    INTERNAL_SERVICE_TOKEN: str
    BACKEND_SERVICE_URL: str

    # SMTP — 결제 확정 시 예약 이메일 발송.
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
    def is_production(self) -> bool:
        return self.ENVIRONMENT.lower() in {"prod", "production"}


settings = Settings()
