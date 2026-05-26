from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.domain.seller.schema.store_sns import StoreSNSInfo
from app.domain.seller.schema.store_operation import StoreOperationTime


class StoreAddressInfo(BaseModel):
    """가게 주소 정보 (nested input)."""
    postal_code: str = Field(..., description="우편번호", min_length=5, max_length=10)
    address: str = Field(..., description="주소", min_length=1, max_length=255)
    detail_address: str = Field(..., description="상세 주소", min_length=1, max_length=255)
    sido: str = Field(..., description="시/도", min_length=1, max_length=50)
    sigungu: str = Field(..., description="시/군/구", min_length=1, max_length=50)
    bname: str = Field(..., description="읍/면/동", min_length=1, max_length=50)
    lat: str = Field(..., description="위도")
    lng: str = Field(..., description="경도")
    nearest_station: Optional[str] = Field(None, description="가장 가까운 역", max_length=100)
    walking_time: Optional[int] = Field(None, description="도보 시간 (분)", ge=0)


class SellerProfileCreateRequest(BaseModel):
    """판매자 회원가입 요청."""
    store_name: str = Field(..., description="매장 이름", min_length=1, max_length=30)
    store_introduction: str = Field(..., description="매장 소개", min_length=1)
    store_phone: str = Field(..., description="매장 전화번호")
    sns_info: Optional[StoreSNSInfo] = Field(None, description="SNS 정보")
    address_info: StoreAddressInfo = Field(..., description="주소 정보")
    operation_times: List[StoreOperationTime] = Field(
        ..., description="요일별 운영 시간", min_length=7, max_length=7,
    )

    @field_validator("operation_times")
    @classmethod
    def validate_operation_times(cls, v):
        days = [op.day_of_week for op in v]
        if len(days) != len(set(days)):
            raise ValueError("중복된 요일이 있습니다.")
        if set(days) != set(range(7)):
            raise ValueError("월요일(0)부터 일요일(6)까지 모든 요일의 운영 정보가 필요합니다.")
        return v


class SellerProfileResponse(BaseModel):
    """판매자 회원가입 응답."""
    store_id: str = Field(..., description="생성된 가게 ID")
    store_name: str = Field(..., description="매장 이름")
    message: str = Field(default="판매자 회원가입이 완료되었습니다.", description="응답 메시지")

    model_config = ConfigDict(from_attributes=True)


class StoreNameUpdateRequest(BaseModel):
    """매장 이름 수정 요청."""
    store_name: str = Field(..., description="매장 이름", min_length=1, max_length=30)


class StoreIntroductionUpdateRequest(BaseModel):
    """매장 설명 수정 요청."""
    store_introduction: str = Field(..., description="매장 소개", min_length=1)


class StorePhoneUpdateRequest(BaseModel):
    """매장 전화번호 수정 요청."""
    store_phone: str = Field(..., description="매장 전화번호")


class StoreProfileResponse(BaseModel):
    """가게 기본 정보 응답."""
    store_id: str = Field(..., description="가게 ID")
    store_name: str = Field(..., description="매장 이름")
    store_introduction: str = Field(..., description="매장 소개")
    store_phone: str = Field(..., description="매장 전화번호")

    model_config = ConfigDict(from_attributes=True)