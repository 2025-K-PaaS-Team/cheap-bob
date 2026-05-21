from fastapi.responses import JSONResponse
from fastapi import APIRouter

from app.domain.auth.cookie import clear_auth_cookie


router = APIRouter()


@router.post("/logout")
async def logout():
    """로그아웃 — 인증 쿠키를 만료시킨다.

    쿠키 정책은 `auth/cookie.py` 의 helper 가 단일 관리한다 (발급/제거 모두 동일 SameSite).
    """
    response = JSONResponse(content={"message": "로그아웃되었습니다."}, status_code=200)
    clear_auth_cookie(response)
    return response
