from fastapi import APIRouter, Request
from pydantic import BaseModel

from api.deps import CurrentUserDep

router = APIRouter()


class TestAuthResponse(BaseModel):
    """JWT 인증 테스트 Response Schema"""
    email: str
    user_type: str
    exp: int
    iat: int


@router.get("/auth", response_model=TestAuthResponse)
async def test_auth(current_user: CurrentUserDep) -> TestAuthResponse:
    """
    JWT Authorization 헤더를 테스트하는 엔드포인트
    인증이 필요합니다
    """
    return TestAuthResponse(
        email=current_user.get("sub"),
        user_type=current_user.get("user_type"),
        exp=current_user.get("exp"),
        iat=current_user.get("iat")
    )