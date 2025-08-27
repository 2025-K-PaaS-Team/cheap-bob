from fastapi import APIRouter, Request
from pydantic import BaseModel


router = APIRouter(prefix="/test", tags=["test"])

class TestAuthResponse(BaseModel):
    """JWT 인증 테스트 Response Schema"""
    email: str
    user_type: str
    exp: int
    iat: int


@router.get("/auth")
async def test_auth(request: Request) -> TestAuthResponse:
    """JWT Authorization 헤더를 테스트하는 엔드포인트"""
    
    user_info = request.state.user
    
    return TestAuthResponse(
        email=user_info.get("sub"),
        user_type=user_info.get("user_type"),
        exp=user_info.get("exp"),
        iat=user_info.get("iat")
    )