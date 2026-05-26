from pydantic import BaseModel, Field


class UserProfileMeResponse(BaseModel):
    """현재 로그인된 사용자 이메일 응답."""

    email: str = Field(..., description="이메일 정보")
