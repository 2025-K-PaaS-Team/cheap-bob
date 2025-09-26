from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, HttpUrl

from schemas.product import ProductResponse
from schemas.image import ImageUploadResponse
from schemas.store_operation import StoreOperationResponse
from schemas.store_settings import StoreAddressResponse


class StoreSNSInfo(BaseModel):
    """가게 SNS 정보"""
    instagram: Optional[HttpUrl] = Field(None, description="인스타그램 URL")
    facebook: Optional[HttpUrl] = Field(None, description="페이스북 URL")
    x: Optional[HttpUrl] = Field(None, description="X(구 트위터) URL")
    homepage: Optional[HttpUrl] = Field(None, description="홈페이지 URL")


class StoreDetailResponse(BaseModel):
    store_id: str = Field(..., description="가게 고유 ID")
    store_name: str = Field(..., description="가게 이름")
    store_introduction: str = Field(..., description="가게 소개")
    store_phone: str = Field(..., description="가게 전화번호")
    seller_email: str = Field(..., description="판매자 이메일")
    created_at: datetime = Field(..., description="가게 생성 시간")
    
    # 주소 정보
    address: StoreAddressResponse = Field(..., description="가게 주소 정보")
    
    # SNS 정보
    sns: StoreSNSInfo = Field(..., description="SNS 정보")
    
    # 운영 시간 정보
    operation_times: List[StoreOperationResponse] = Field(..., description="요일별 운영 시간")
    
    # 이미지 정보
    images: List[ImageUploadResponse] = Field(..., description="가게 이미지 목록")
    
    # 상품 정보
    products: List[ProductResponse] = Field(..., description="가게 상품 목록")
    
    class Config:
        from_attributes = True


class StoreDetailResponseForCustomer(StoreDetailResponse):
    """고객용 가게 상세 정보 (즐겨찾기 정보 포함)"""
    is_favorite: bool = Field(False, description="즐겨찾기 등록 여부")
    
class StoreFavoriteStateResponse(BaseModel):
    """고객 즐겨찾기 추가/삭제 성공 메시지"""
    message: str = Field(..., description="즐겨찾기 추가/삭제 성공 메시지")
    
class StoreCloseStateResponse(BaseModel):
    """가게 마감 성공 메시지"""
    success: bool = Field(..., description="가게 마감 성공 상태")
    message: str = Field(..., description="가게 마감 성공 메시지")
    refunded_orders: int = Field(..., description="환불된 주문 건 수")