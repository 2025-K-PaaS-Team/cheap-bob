from typing import List, Optional
from datetime import time
from pydantic import BaseModel, Field, model_validator


class StoreAddressUpdateRequest(BaseModel):
    """주소 수정 요청"""
    postal_code: str = Field(..., description="우편번호", min_length=5, max_length=10)
    address: str = Field(..., description="주소", min_length=1, max_length=255)
    detail_address: str = Field(..., description="상세 주소", min_length=1, max_length=255)
    sido: str = Field(..., description="시/도", min_length=1, max_length=50)
    sigungu: str = Field(..., description="시/군/구", min_length=1, max_length=50)
    bname: str = Field(..., description="읍/면/동", min_length=1, max_length=50)
    lat: str = Field(..., description="위도")
    lng: str = Field(..., description="경도")


class StorePaymentUpdateRequest(BaseModel):
    """결제 정보 수정 요청"""
    portone_store_id: str = Field(..., description="포트원 가게 ID")
    portone_channel_id: str = Field(..., description="포트원 채널 ID")


class StoreDayOperationUpdateRequest(BaseModel):
    """특정 요일 운영 정보 수정 요청"""
    is_open_enabled: bool = Field(..., description="해당 요일 운영 여부")
    open_time: time = Field(default=time(1, 0), description="오픈 시간")
    pickup_start_time: time = Field(default=time(2, 0), description="픽업 시작 시간")
    pickup_end_time: time = Field(default=time(3, 0), description="픽업 종료 시간")
    close_time: time = Field(default=time(4, 0), description="마감 시간")
    
    @model_validator(mode='after')
    def validate_times(self):
        if self.is_open_enabled:
            # 활성화 시 모든 시간이 필요
            if not all([self.open_time, self.close_time, 
                       self.pickup_start_time, self.pickup_end_time]):
                missing_fields = []
                if not self.open_time: missing_fields.append('open_time')
                if not self.close_time: missing_fields.append('close_time')
                if not self.pickup_start_time: missing_fields.append('pickup_start_time')
                if not self.pickup_end_time: missing_fields.append('pickup_end_time')
                
                raise ValueError(f"운영 활성화 시 다음 필드가 필요합니다: {', '.join(missing_fields)}")
            
            # 시간 유효성 검증
            if self.open_time >= self.close_time:
                raise ValueError("오픈 시간은 마감 시간보다 이전이어야 합니다.")
            
            if self.pickup_start_time < self.open_time or self.pickup_start_time >= self.close_time:
                raise ValueError("픽업 시작 시간은 오픈 시간 이후, 마감 시간 이전이어야 합니다.")
            
            if self.pickup_end_time <= self.pickup_start_time:
                raise ValueError("픽업 종료 시간은 픽업 시작 시간보다 이후여야 합니다.")
            
            if self.pickup_end_time > self.close_time:
                raise ValueError("픽업 종료 시간은 마감 시간 이전이어야 합니다.")
        
        return self


# Response Models
class StoreAddressResponse(BaseModel):
    """주소 정보 응답"""
    store_id: str = Field(..., description="가게 ID")
    postal_code: str = Field(..., description="우편번호")
    address: str = Field(..., description="주소")
    detail_address: str = Field(..., description="상세 주소")
    sido: str = Field(..., description="시/도")
    sigungu: str = Field(..., description="시/군/구")
    bname: str = Field(..., description="읍/면/동")
    lat: str = Field(..., description="위도")
    lng: str = Field(..., description="경도")
    
    class Config:
        from_attributes = True


class StorePaymentResponse(BaseModel):
    """결제 정보 응답"""
    store_id: str = Field(..., description="가게 ID")
    portone_store_id: str = Field(..., description="포트원 가게 ID")
    portone_channel_id: str = Field(..., description="포트원 채널 ID")
    
    class Config:
        from_attributes = True


class StoreOperationResponse(BaseModel):
    """운영 정보 응답"""
    day_of_week: int = Field(..., ge=0, le=6, description="요일 (0: 월요일, 6: 일요일)")
    open_time: time = Field(..., description="오픈 시간")
    close_time: time = Field(..., description="마감 시간")
    pickup_start_time: time = Field(..., description="픽업 시작 시간")
    pickup_end_time: time = Field(..., description="픽업 종료 시간")
    is_open_enabled: bool = Field(..., description="해당 요일 운영 여부")
    
    class Config:
        from_attributes = True