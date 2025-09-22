from typing import List, Optional
from datetime import time
from pydantic import BaseModel, Field, field_validator, HttpUrl, model_validator


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
    pickup_start_time: time = Field(default=time(2, 0), description="픽업 시작 시간")
    pickup_end_time: time = Field(default=time(3, 0), description="픽업 종료 시간")
    close_time: time = Field(default=time(4, 0), description="마감 시간")
    is_open_enabled: bool = Field(..., description="해당 요일 운영 여부")
    
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

class StorePaymentInfoCreateRequest(BaseModel):
    portone_store_id: str = Field(..., description="포트원 가게 ID")
    portone_channel_id: str = Field(..., description="포트원 채널 ID")
    portone_secret_key: str = Field(..., description="포트원 시크릿 키")

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
    
    # 결제 정보
    payment_info: StorePaymentInfoCreateRequest = Field(..., description="결제 정보")
    
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


class StoreNameUpdateRequest(BaseModel):
    """매장 이름 수정 요청"""
    store_name: str = Field(..., description="매장 이름", min_length=1, max_length=20)


class StoreIntroductionUpdateRequest(BaseModel):
    """매장 설명 수정 요청"""
    store_introduction: str = Field(..., description="매장 소개", min_length=1)


class StorePhoneUpdateRequest(BaseModel):
    """매장 전화번호 수정 요청"""
    store_phone: str = Field(..., description="매장 전화번호")


class StoreProfileResponse(BaseModel):
    """가게 기본 정보 응답"""
    store_id: str = Field(..., description="가게 ID")
    store_name: str = Field(..., description="매장 이름")
    store_introduction: str = Field(..., description="매장 소개")
    store_phone: str = Field(..., description="매장 전화번호")
    
    class Config:
        from_attributes = True