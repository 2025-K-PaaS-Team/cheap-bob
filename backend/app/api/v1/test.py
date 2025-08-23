from fastapi import APIRouter, Request

router = APIRouter(prefix="/test", tags=["test"])


@router.get("/cookie")
async def test_cookie(request: Request):
    """JWT 쿠키를 테스트하는 엔드포인트"""
    
    user_info = request.state.user
    
    return {
        "email": user_info.get("sub"),
        "user_type": user_info.get("user_type"),
        "exp": user_info.get("exp"),
        "iat": user_info.get("iat")
    }