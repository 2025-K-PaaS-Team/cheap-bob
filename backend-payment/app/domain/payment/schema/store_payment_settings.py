from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class StorePaymentInfoCreateRequest(BaseModel):
    """1차 가입의 결제 정보 등록 요청 — ID 3종 + secret_key."""
    portone_store_id: str = Field(..., description="포트원 가게 ID")
    portone_channel_id: str = Field(..., description="포트원 채널 ID")
    portone_secret_key: str = Field(..., min_length=1, description="포트원 시크릿 키")


class StorePaymentInfoCheckResponse(BaseModel):
    is_exist: bool = Field(..., description="결제 정보 등록 여부")


class StorePaymentUpdateRequest(BaseModel):
    portone_store_id: str = Field(..., description="포트원 가게 ID")
    portone_channel_id: str = Field(..., description="포트원 채널 ID")


class StorePaymentSecretUpdateRequest(BaseModel):
    portone_secret_key: str = Field(..., min_length=1, description="포트원 시크릿 키")


class StoreInitPaymentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    store_id: str = Field(..., description="가게 ID")
    portone_store_id: Optional[str] = Field(None, description="포트원 가게 ID")
    portone_channel_id: Optional[str] = Field(None, description="포트원 채널 ID")


class StorePaymentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    store_id: str = Field(..., description="가게 ID")
    portone_store_id: str = Field(..., description="포트원 가게 ID")
    portone_channel_id: str = Field(..., description="포트원 채널 ID")
