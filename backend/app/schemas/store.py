from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

class StoreResponse(BaseModel):
    store_id: str = Field(..., description="가게 고유 ID")
    store_name: str = Field(..., description="가게 이름")
    seller_email: str = Field(..., description="판매자 이메일")
    created_at: datetime = Field(..., description="가게 생성 시간")
    
    class Config:
        from_attributes = True