"""테스트 전역 부트스트랩.

``pydantic_settings.Settings`` 가 모듈 로드 시점에 모든 env 를 강제 요구하므로, 실 ``.env``
없는 환경에서도 테스트 import 가 성공하도록 더미값을 채워둔다. ``setdefault`` 라 실 env
설정이 있으면 그대로 존중한다 — 통합 테스트의 ``POSTGRES_TEST_URL`` 같은 값을 덮어쓰지 않는다.

본 conftest 는 ``backend/test/`` 루트라 unit / integration 양쪽 하위 conftest 보다 먼저 로드된다.
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
    "REDIS_HOST": "localhost",
    "REDIS_PORT": "6379",
    "REDIS_DB": "0",
    "MONGODB_HOST": "localhost",
    "MONGODB_PORT": "27017",
    "MONGODB_USER": "test",
    "MONGODB_PASSWORD": "test",
    "MONGODB_NAME": "test",
    "GOOGLE_CLIENT_ID": "test",
    "GOOGLE_CLIENT_SECRET": "test",
    "KAKAO_CLIENT_ID": "test",
    "KAKAO_CLIENT_SECRET": "test",
    "NAVER_CLIENT_ID": "test",
    "NAVER_CLIENT_SECRET": "test",
    "OAUTH_REDIRECT_BASE_URL": "http://localhost:8000",
    "JWT_SECRET": "unit-test-jwt-secret-please-do-not-use-in-prod",
    "JWT_ALGORITHM": "HS256",
    "MAX_RETRY_LOCK": "3",
    "AWS_ACCESS_KEY_ID": "test",
    "AWS_SECRET_ACCESS_KEY": "test",
    "AWS_REGION": "ap-northeast-2",
    "AWS_S3_BUCKET_NAME": "test",
    "AWS_S3_ENDPOINT_URL": "http://localhost:9000",
    "SUPER_ADMIN_SMTP_USER": "test",
    "SUPER_ADMIN_SMTP_PASSWORD": "test",
    "SUPER_ADMIN_SMTP_EMAIL": "test@example.com",
    "SUPER_ADMIN_SMTP_HOST": "smtp.example.com",
    "SUPER_ADMIN_SMTP_PORT": "587",
    "SUPER_ADMIN_SMTP_NAME": "test",
}
for _k, _v in _DEFAULTS.items():
    os.environ.setdefault(_k, _v)
