from pydantic import BaseModel, Field

class UserProfileMeResponse(BaseModel):
    """유저 이메일 응답 스키마"""
    email: str = Field(..., description="이메일 정보")