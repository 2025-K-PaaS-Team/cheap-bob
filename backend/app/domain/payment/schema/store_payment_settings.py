from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class StorePaymentInfoCreateRequest(BaseModel):
    """1차 가입의 결제 정보 등록 요청 — ID 3종 + secret_key 한 번에 받는다."""
    portone_store_id: str = Field(..., description="포트원 가게 ID")
    portone_channel_id: str = Field(..., description="포트원 채널 ID")
    portone_secret_key: str = Field(..., min_length=1, description="포트원 시크릿 키")


class StorePaymentInfoCheckResponse(BaseModel):
    """1차 가입 흐름에서 결제 정보 등록 여부 확인."""
    is_exist: bool = Field(..., description="결제 정보 등록 여부")


class StorePaymentUpdateRequest(BaseModel):
    portone_store_id: str = Field(..., description="포트원 가게 ID")
    portone_channel_id: str = Field(..., description="포트원 채널 ID")


class StorePaymentSecretUpdateRequest(BaseModel):
    """seller 가 PortOne 콘솔에서 secret key rotate 한 경우 갱신."""
    portone_secret_key: str = Field(..., min_length=1, description="포트원 시크릿 키")


class StoreInitPaymentResponse(BaseModel):
    """결제 정보 조회 (None 허용). secret_key 는 절대 노출하지 않는다."""
    model_config = ConfigDict(from_attributes=True)

    store_id: str = Field(..., description="가게 ID")
    portone_store_id: Optional[str] = Field(None, description="포트원 가게 ID")
    portone_channel_id: Optional[str] = Field(None, description="포트원 채널 ID")


class StorePaymentResponse(BaseModel):
    """결제 정보 응답. secret_key 는 절대 노출하지 않는다."""
    model_config = ConfigDict(from_attributes=True)

    store_id: str = Field(..., description="가게 ID")
    portone_store_id: str = Field(..., description="포트원 가게 ID")
    portone_channel_id: str = Field(..., description="포트원 채널 ID")
