from fastapi.responses import JSONResponse
from fastapi import APIRouter, Query

from app.config.setting import settings


router = APIRouter()


@router.post("/logout")
async def logout(state: str = Query(None, description="로컬 테스트 분기용 (dev only)")):
    """로그아웃 — 인증 쿠키를 만료시킨다.

    dev 환경의 SameSite=None 경로와 prod 의 SameSite=lax 경로를 분리한다 (state == '1004' 분기).
    """
    response = JSONResponse(content={"message": "로그아웃되었습니다."}, status_code=200)
    samesite = "none" if (state == "1004" and settings.ENVIRONMENT == "dev") else "lax"
    response.set_cookie(
        key="access_token",
        value="",
        httponly=True,
        secure=True,
        samesite=samesite,
        max_age=0,
        path="/",
    )
    return response
