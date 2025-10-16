from typing import List
from pydantic import BaseModel, Field


class ImageUploadResponse(BaseModel):
    """이미지 업로드 응답"""
    image_id: str = Field(..., description="이미지 ID (S3 키)")
    image_url: str = Field(..., description="이미지 URL")
    is_main: bool = Field(..., description="대표 이미지 여부")
    display_order: int = Field(..., description="표시 순서")


class StoreImagesUploadResponse(BaseModel):
    """가게 이미지 업로드 응답"""
    store_id: str = Field(..., description="가게 ID")
    images: List[ImageUploadResponse] = Field(..., description="업로드된 이미지 목록")
    total: int = Field(..., description="업로드된 이미지 총 개수")


class StoreImagesResponse(BaseModel):
    """가게 이미지 목록 응답"""
    store_id: str = Field(..., description="가게 ID")
    images: List[ImageUploadResponse] = Field(..., description="이미지 목록")
    total: int = Field(..., description="이미지 총 개수")
    
    class Config:
        from_attributes = True