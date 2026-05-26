from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class StoreSNSInfo(BaseModel):
    """가게 SNS 정보 (nested input/output). store_id 없이 4개 URL만 포함."""
    instagram: Optional[HttpUrl] = Field(None, description="인스타그램 URL")
    facebook: Optional[HttpUrl] = Field(None, description="페이스북 URL")
    x: Optional[HttpUrl] = Field(None, description="X(구 트위터) URL")
    homepage: Optional[HttpUrl] = Field(None, description="홈페이지 URL")


class StoreSNSUpdateRequest(StoreSNSInfo):
    """SNS 정보 수정 요청."""


class StoreSNSResponse(StoreSNSInfo):
    """SNS 정보 응답 — store_id 포함."""
    store_id: str = Field(..., description="가게 ID")

    model_config = ConfigDict(from_attributes=True)