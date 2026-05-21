from pydantic import BaseModel, ConfigDict, Field, model_validator
from datetime import time, datetime


class StoreOperationTime(BaseModel):
    """요일별 운영 시간 (nested input)."""
    day_of_week: int = Field(..., ge=0, le=6, description="요일 (0: 월요일, 6: 일요일)")
    open_time: time = Field(default=time(1, 0), description="오픈 시간")
    pickup_start_time: time = Field(default=time(2, 0), description="픽업 시작 시간")
    pickup_end_time: time = Field(default=time(3, 0), description="픽업 종료 시간")
    close_time: time = Field(default=time(4, 0), description="마감 시간")
    is_open_enabled: bool = Field(..., description="해당 요일 운영 여부")

    @model_validator(mode="after")
    def validate_times(self):
        if not self.is_open_enabled:
            return self

        if self.open_time >= self.close_time:
            raise ValueError("오픈 시간은 마감 시간보다 이전이어야 합니다.")
        if self.pickup_start_time < self.open_time or self.pickup_start_time >= self.close_time:
            raise ValueError("픽업 시작 시간은 오픈 시간 이후, 마감 시간 이전이어야 합니다.")
        if self.pickup_end_time <= self.pickup_start_time:
            raise ValueError("픽업 종료 시간은 픽업 시작 시간보다 이후여야 합니다.")
        if self.pickup_end_time > self.close_time:
            raise ValueError("픽업 종료 시간은 마감 시간 이전이어야 합니다.")
        return self


class StoreOperationResponse(BaseModel):
    """운영 정보 응답."""
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

    model_config = ConfigDict(from_attributes=True)