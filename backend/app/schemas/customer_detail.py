from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class CustomerDetailBase(BaseModel):
    """고객 상세 정보 기본 스키마"""
    nickname: str = Field(..., min_length=1, max_length=7, description="닉네임 (1-7자)")
    phone_number: str = Field(..., pattern="^[0-9]{11}$", description="전화번호 (11자리 숫자)")
    
    @field_validator('phone_number')
    def validate_phone_number(cls, v):
        if not v.isdigit() or len(v) != 11:
            raise ValueError("전화번호는 11자리 숫자여야 합니다")
        return v


class CustomerDetailCreate(CustomerDetailBase):
    """고객 상세 정보 생성 스키마"""
    pass


class CustomerDetailUpdate(BaseModel):
    """고객 상세 정보 수정 스키마"""
    nickname: Optional[str] = Field(None, min_length=1, max_length=7, description="닉네임 (1-7자)")
    phone_number: Optional[str] = Field(None, pattern="^[0-9]{11}$", description="전화번호 (11자리 숫자)")
    
    @field_validator('phone_number')
    def validate_phone_number(cls, v):
        if v and (not v.isdigit() or len(v) != 11):
            raise ValueError("전화번호는 11자리 숫자여야 합니다")
        return v


class CustomerDetailResponse(CustomerDetailBase):
    """고객 상세 정보 응답 스키마"""
    customer_email: str = Field(..., description="사용자 이메일")
    created_at: datetime = Field(..., description="최초 생성 일자")
    updated_at: datetime = Field(..., description="수정 일자")
    
    model_config = {
        "from_attributes": True
    }