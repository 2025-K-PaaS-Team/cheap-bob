from typing import List, Optional
from datetime import time, datetime
from pydantic import BaseModel, Field, field_validator


class OperationTimeSchema(BaseModel):
    """운영 시간 스키마"""
    day_of_week: int = Field(..., ge=0, le=6, description="요일 (0: 월요일, 6: 일요일)")
    open_time: time = Field(..., description="오픈 시간")
    close_time: time = Field(..., description="마감 시간")
    pickup_start_time: time = Field(..., description="픽업 시작 시간")
    pickup_end_time: time = Field(..., description="픽업 종료 시간")
    is_open_enabled: bool = Field(..., description="운영 활성화 여부")
    
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


class StoreOperationCreateRequest(BaseModel):
    """가게 운영 정보 생성 요청"""
    store_id: str = Field(..., description="가게 ID")
    operation_times: List[OperationTimeSchema] = Field(..., description="요일별 운영 시간 목록")
    
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


class StoreOperationUpdateRequest(BaseModel):
    """운영 시간 업데이트 요청"""
    open_time: Optional[time] = Field(None, description="오픈 시간")
    close_time: Optional[time] = Field(None, description="마감 시간")
    pickup_start_time: Optional[time] = Field(None, description="픽업 시작 시간")
    pickup_end_time: Optional[time] = Field(None, description="픽업 종료 시간")
    is_open_enabled: Optional[bool] = Field(None, description="운영 활성화 여부")


class StoreOperationModificationRequest(BaseModel):
    """운영 정보 수정 예약 요청"""
    operation_id: int = Field(..., description="운영 정보 ID")
    new_open_time: Optional[time] = Field(None, description="새 오픈 시간")
    new_close_time: Optional[time] = Field(None, description="새 마감 시간")
    new_pickup_start_time: Optional[time] = Field(None, description="새 픽업 시작 시간")
    new_pickup_end_time: Optional[time] = Field(None, description="새 픽업 종료 시간")
    new_is_open_enabled: Optional[bool] = Field(None, description="새 운영 활성화 여부")


class StoreOperationResponse(BaseModel):
    """운영 정보 응답"""
    operation_id: int
    store_id: str
    day_of_week: int
    open_time: time
    close_time: time
    pickup_start_time: time
    pickup_end_time: time
    is_open_enabled: bool
    is_currently_open: bool
    updated_at: datetime
    
    class Config:
        from_attributes = True
    

class StoreOperationModificationResponse(BaseModel):
    """운영 정보 수정 예약 응답"""
    modification_id: int
    operation_id: int
    new_open_time: Optional[time]
    new_close_time: Optional[time]
    new_pickup_start_time: Optional[time]
    new_pickup_end_time: Optional[time]
    new_is_open_enabled: Optional[bool]
    created_at: datetime
    
    class Config:
        from_attributes = True