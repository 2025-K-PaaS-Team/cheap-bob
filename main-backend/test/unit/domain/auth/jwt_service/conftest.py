import pytest

from app.domain.auth.service.jwt import JwtService


@pytest.fixture
def service() -> JwtService:
    """JwtService 는 stateless — 매 테스트마다 새로 생성해도 부담 없다."""
    return JwtService()
