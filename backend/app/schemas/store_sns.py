from typing import Optional
from pydantic import BaseModel, Field, HttpUrl

class StoreSNSUpdateRequest(BaseModel):
    """SNS 정보 수정 요청"""
    instagram: Optional[HttpUrl] = Field(None, description="인스타그램 URL")
    facebook: Optional[HttpUrl] = Field(None, description="페이스북 URL")
    x: Optional[HttpUrl] = Field(None, description="X(구 트위터) URL")
    homepage: Optional[HttpUrl] = Field(None, description="홈페이지 URL")


class StoreSNSResponse(BaseModel):
    """SNS 정보 응답"""
    store_id: str = Field(..., description="가게 ID")
    instagram: Optional[HttpUrl] = Field(None, description="인스타그램 URL")
    facebook: Optional[HttpUrl] = Field(None, description="페이스북 URL")
    x: Optional[HttpUrl] = Field(None, description="X(구 트위터) URL")
    homepage: Optional[HttpUrl] = Field(None, description="홈페이지 URL")
    
    class Config:
        from_attributes = True