from typing import List, Optional
from datetime import time
from pydantic import BaseModel, Field, field_validator, HttpUrl


class StoreSNSInfo(BaseModel):
    """가게 SNS 정보"""
    instagram: Optional[HttpUrl] = Field(None, description="인스타그램 URL")
    facebook: Optional[HttpUrl] = Field(None, description="페이스북 URL")
    x: Optional[HttpUrl] = Field(None, description="X(구 트위터) URL")
    homepage: Optional[HttpUrl] = Field(None, description="홈페이지 URL")


class StoreAddressInfo(BaseModel):
    """가게 주소 정보"""
    postal_code: str = Field(..., description="우편번호", min_length=5, max_length=10)
    address: str = Field(..., description="주소", min_length=1, max_length=255)
    detail_address: str = Field(..., description="상세 주소", min_length=1, max_length=255)
    sido: str = Field(..., description="시/도", min_length=1, max_length=50)
    sigungu: str = Field(..., description="시/군/구", min_length=1, max_length=50)
    bname: str = Field(..., description="읍/면/동", min_length=1, max_length=50)
    lat: str = Field(..., description="위도")
    lng: str = Field(..., description="경도")


class StoreOperationTime(BaseModel):
    """요일별 운영 시간"""
    day_of_week: int = Field(..., ge=0, le=6, description="요일 (0: 월요일, 6: 일요일)")
    open_time: time = Field(default=time(1, 0), description="오픈 시간")
    close_time: time = Field(default=time(2, 0), description="마감 시간") 
    pickup_start_time: time = Field(default=time(3, 0), description="픽업 시작 시간")
    pickup_end_time: time = Field(default=time(4, 0), description="픽업 종료 시간")
    is_open_enabled: bool = Field(..., description="해당 요일 운영 여부")
    
    @field_validator('open_time', 'close_time', 'pickup_start_time', 'pickup_end_time')
    @classmethod
    def validate_times(cls, v, info):
        values = info.data
        
        # 모든 시간이 입력된 경우에만 검증
        if all(key in values for key in ['open_time', 'close_time', 'pickup_start_time', 'pickup_end_time']):
            open_time = values.get('open_time')
            close_time = values.get('close_time')
            pickup_start = values.get('pickup_start_time')
            pickup_end = values.get('pickup_end_time')
            
            # 오픈 시간 < 마감 시간
            if open_time and close_time and open_time >= close_time:
                raise ValueError("오픈 시간은 마감 시간보다 이전이어야 합니다.")
            
            # 픽업 시작 >= 오픈 시간 AND 픽업 시작 < 마감 시간
            if pickup_start and open_time and close_time:
                if pickup_start < open_time or pickup_start >= close_time:
                    raise ValueError("픽업 시작 시간은 오픈 시간 이후, 마감 시간 이전이어야 합니다.")
            
            # 픽업 종료 > 픽업 시작 AND 픽업 종료 <= 마감 시간
            if pickup_end and pickup_start and close_time:
                if pickup_end <= pickup_start:
                    raise ValueError("픽업 종료 시간은 픽업 시작 시간보다 이후여야 합니다.")
                if pickup_end > close_time:
                    raise ValueError("픽업 종료 시간은 마감 시간 이전이어야 합니다.")
        
        return v


class SellerProfileCreateRequest(BaseModel):
    """판매자 회원가입 요청"""
    # 매장 기본 정보
    store_name: str = Field(..., description="매장 이름", min_length=1, max_length=20)
    store_introduction: str = Field(..., description="매장 소개", min_length=1)
    store_phone: str = Field(..., description="매장 전화번호")
    
    # SNS 정보
    sns_info: Optional[StoreSNSInfo] = Field(None, description="SNS 정보")
    
    # 주소 정보
    address_info: StoreAddressInfo = Field(..., description="주소 정보")
    
    # 운영 정보
    operation_times: List[StoreOperationTime] = Field(..., description="요일별 운영 시간", min_items=7, max_items=7)
    
    @field_validator('operation_times')
    @classmethod
    def validate_operation_times(cls, v):
        # 중복 요일 체크
        days = [op.day_of_week for op in v]
        if len(days) != len(set(days)):
            raise ValueError("중복된 요일이 있습니다.")
        
        # 모든 요일(0-6)이 있는지 체크
        if set(days) != set(range(7)):
            raise ValueError("월요일(0)부터 일요일(6)까지 모든 요일의 운영 정보가 필요합니다.")
        
        return v


class SellerProfileResponse(BaseModel):
    """판매자 회원가입 응답"""
    store_id: str = Field(..., description="생성된 가게 ID")
    store_name: str = Field(..., description="매장 이름")
    message: str = Field(default="판매자 회원가입이 완료되었습니다.", description="응답 메시지")
    
    class Config:
        from_attributes = True