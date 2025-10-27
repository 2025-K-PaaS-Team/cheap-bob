from pydantic import BaseModel, Field


class UserRoleResponse(BaseModel):
    """사용자 역할 응답 스키마"""
    email: str = Field(..., description="사용자 이메일")
    user_type: str = Field(..., description="사용자 유형 (customer/seller)")
    is_active: bool = Field(..., description="계정 활성화 상태")