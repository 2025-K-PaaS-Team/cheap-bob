"""service-to-service 인증 dependency.

/api/internal/* 경로는 JWT 가 아니라 X-Internal-Token 헤더로 인가한다. 양쪽 서비스가
같은 INTERNAL_SERVICE_TOKEN 환경변수를 공유하며, 헤더가 일치해야 통과.
"""
from fastapi import Header, HTTPException, status

from app.config.setting import settings


async def require_internal_token(
    x_internal_token: str = Header(..., alias="X-Internal-Token"),
) -> None:
    if x_internal_token != settings.INTERNAL_SERVICE_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid internal token",
        )
