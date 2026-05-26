"""테스트 전역 부트스트랩 — payment-backend.

``pydantic_settings.Settings`` 가 모듈 로드 시점에 모든 env 를 강제 요구하므로, 실 ``.env``
없는 환경에서도 테스트 import 가 성공하도록 더미값을 채워둔다.
"""
import os


_DEFAULTS = {
    "DEBUG": "false",
    "ENVIRONMENT": "test",
    "FRONTEND_URL": "http://localhost:3000",
    "FRONTEND_LOCAL_URL": "http://localhost:3000",
    "DB_HOST": "localhost",
    "DB_PORT": "5432",
    "DB_USER": "test",
    "DB_PASSWORD": "test",
    "DB_NAME": "test",
    "JWT_SECRET": "unit-test-jwt-secret-please-do-not-use-in-prod",
    "JWT_ALGORITHM": "HS256",
    "MAX_RETRY_LOCK": "3",
    "INTERNAL_SERVICE_TOKEN": "test-internal-token",
    "BACKEND_SERVICE_URL": "http://localhost:8000",
    "SUPER_ADMIN_SMTP_USER": "test",
    "SUPER_ADMIN_SMTP_PASSWORD": "test",
    "SUPER_ADMIN_SMTP_EMAIL": "test@example.com",
    "SUPER_ADMIN_SMTP_HOST": "smtp.example.com",
    "SUPER_ADMIN_SMTP_PORT": "587",
    "SUPER_ADMIN_SMTP_NAME": "test",
}
for _k, _v in _DEFAULTS.items():
    os.environ.setdefault(_k, _v)
