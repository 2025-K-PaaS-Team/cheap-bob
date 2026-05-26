from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime


class CustomerDetailBase(BaseModel):
    """공통 검증 규칙 (닉네임 1-7자, 전화번호 11자리 숫자)."""
    nickname: str = Field(..., min_length=1, max_length=7, description="닉네임 (1-7자)")
    phone_number: str = Field(
        ..., pattern="^[0-9]{11}$", description="전화번호 (11자리 숫자)",
    )


class CustomerDetailUpdateRequest(BaseModel):
    """PATCH — 일부 필드만 전달 가능."""
    nickname: Optional[str] = Field(None, min_length=1, max_length=7)
    phone_number: Optional[str] = Field(None, pattern="^[0-9]{11}$")


class CustomerDetailResponse(CustomerDetailBase):
    customer_email: str = Field(..., description="사용자 이메일")
    created_at: datetime = Field(..., description="최초 생성 일시")
    updated_at: datetime = Field(..., description="최종 수정 일시")

    model_config = {"from_attributes": True}
