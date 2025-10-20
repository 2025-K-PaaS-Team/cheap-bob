from typing import List, Optional
from datetime import time, datetime
from pydantic import BaseModel, Field, model_validator
from schemas.store_operation import StoreOperationTime

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
    nearest_station: Optional[str] = Field(None, description="가장 가까운 역", max_length=100)
    walking_time: Optional[int] = Field(None, description="도보 시간 (분)", ge=0)


class StorePaymentUpdateRequest(BaseModel):
    """결제 정보 수정 요청"""
    portone_store_id: str = Field(..., description="포트원 가게 ID")
    portone_channel_id: str = Field(..., description="포트원 채널 ID")


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
    nearest_station: Optional[str] = Field(None, description="가장 가까운 역")
    walking_time: Optional[int] = Field(None, description="도보 시간 (분)")
    
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


class StoreOperationReservationRequest(BaseModel):
    """운영 정보 예약 요청 (월요일부터 일요일까지 모든 요일 정보 필수)"""
    operation_times: List[StoreOperationTime] = Field(
        ..., 
        min_length=7, 
        max_length=7,
        description="요일별 운영 시간 (월요일부터 일요일까지 7개 필수)"
    )
    
    @model_validator(mode='after')
    def validate_all_days(self):
        # 요일 중복 검사
        days = [op.day_of_week for op in self.operation_times]
        if len(set(days)) != 7:
            raise ValueError("모든 요일(0-6)에 대한 정보가 필요합니다.")
        
        # 0-6 범위 확인
        if set(days) != set(range(7)):
            missing_days = set(range(7)) - set(days)
            raise ValueError(f"누락된 요일이 있습니다: {sorted(missing_days)}")
        
        return self


class StoreOperationReservationUpdateRequest(BaseModel):
    """운영 정보 예약 수정 요청"""
    operation_times: List[StoreOperationTime] = Field(
        ..., 
        min_length=7, 
        max_length=7,
        description="요일별 운영 시간 (월요일부터 일요일까지 7개 필수)"
    )
    
    @model_validator(mode='after')
    def validate_all_days(self):
        # 요일 중복 검사
        days = [op.day_of_week for op in self.operation_times]
        if len(set(days)) != 7:
            raise ValueError("모든 요일(0-6)에 대한 정보가 필요합니다.")
        
        # 0-6 범위 확인
        if set(days) != set(range(7)):
            missing_days = set(range(7)) - set(days)
            raise ValueError(f"누락된 요일이 있습니다: {sorted(missing_days)}")
        
        return self


class StoreOperationModificationResponse(BaseModel):
    """운영 정보 수정 예약 응답"""
    modification_id: int = Field(..., description="수정 예약 ID")
    operation_id: int = Field(..., description="운영 정보 ID") 
    day_of_week: int = Field(..., ge=0, le=6, description="요일 (0: 월요일, 6: 일요일)")
    new_open_time: Optional[time] = Field(None, description="변경될 오픈 시간")
    new_close_time: Optional[time] = Field(None, description="변경될 마감 시간")
    new_pickup_start_time: Optional[time] = Field(None, description="변경될 픽업 시작 시간")
    new_pickup_end_time: Optional[time] = Field(None, description="변경될 픽업 종료 시간")
    new_is_open_enabled: Optional[bool] = Field(None, description="변경될 운영 여부")
    created_at: datetime = Field(..., description="예약 생성 시간")
    
    class Config:
        from_attributes = True


class StoreOperationReservationResponse(BaseModel):
    """운영 정보 예약 조회 응답"""
    modifications: List[StoreOperationModificationResponse] = Field(
        ..., 
        description="예약된 운영 정보 변경사항 목록"
    )