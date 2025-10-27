from typing import Literal
from pydantic import BaseModel, Field


class UserRoleResponse(BaseModel):
    """사용자 역할 응답 스키마"""
    email: str = Field(..., description="사용자 이메일")
    user_type: str = Field(..., description="사용자 유형 (customer/seller)")
    is_active: bool = Field(..., description="계정 활성화 상태")
    status: Literal["profile", "store", "product", "complete"] = Field(
        ..., 
        description="등록 상태 (customer - profile: 프로필 미등록, complete: 등록 완료 / seller - store: 가게 미등록, product: 상품 미등록, complete: 등록 완료)"
    )