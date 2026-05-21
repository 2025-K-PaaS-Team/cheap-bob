from typing import Optional
from pydantic import BaseModel, Field


class StorePaymentInfoCreateRequest(BaseModel):
    """1차 가입의 결제 정보 등록 요청."""
    portone_store_id: str = Field(..., description="포트원 가게 ID")
    portone_channel_id: str = Field(..., description="포트원 채널 ID")
    portone_secret_key: str = Field(..., description="포트원 시크릿 키")


class StorePaymentInfoCheckResponse(BaseModel):
    is_exist: bool = Field(..., description="결제 정보 등록 여부")


class StorePaymentUpdateRequest(BaseModel):
    portone_store_id: str = Field(..., description="포트원 가게 ID")
    portone_channel_id: str = Field(..., description="포트원 채널 ID")


class StoreInitPaymentResponse(BaseModel):
    """결제 정보 조회 (None 허용)."""
    store_id: str = Field(..., description="가게 ID")
    portone_store_id: Optional[str] = Field(None, description="포트원 가게 ID")
    portone_channel_id: Optional[str] = Field(None, description="포트원 채널 ID")


    class Config:
        from_attributes = True


class StorePaymentResponse(BaseModel):
    """결제 정보 응답."""
    store_id: str = Field(..., description="가게 ID")
    portone_store_id: str = Field(..., description="포트원 가게 ID")
    portone_channel_id: str = Field(..., description="포트원 채널 ID")


    class Config:
        from_attributes = True
