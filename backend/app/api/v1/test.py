from fastapi import APIRouter, Request
from pydantic import BaseModel


router = APIRouter(prefix="/test", tags=["test"])

class TestCookieResponse(BaseModel):
    """쿠키 테스트 Response Schema"""
    email: str
    user_type: str
    exp: int
    iat: int


@router.get("/cookie")
async def test_cookie(request: Request) -> TestCookieResponse:
    """JWT 쿠키를 테스트하는 엔드포인트"""
    
    user_info = request.state.user
    
    return TestCookieResponse(
        email=user_info.get("sub"),
        user_type=user_info.get("user_type"),
        exp=user_info.get("exp"),
        iat=user_info.get("iat")
    )