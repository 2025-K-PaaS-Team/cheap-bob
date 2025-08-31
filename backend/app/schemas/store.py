from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class StoreProductResponse(BaseModel):
    product_id: str = Field(..., description="상품 고유 ID")
    product_name: str = Field(..., description="상품 이름")
    initial_stock: int = Field(..., description="상품 설정 수량")
    current_stock: int = Field(..., description="현재 남은 상품 수량")
    price: int = Field(..., description="상품 가격 (원 단위)")
    sale: Optional[int] = Field(None, description="세일 퍼센트")
    
    class Config:
        from_attributes = True


class StoreCreateRequest(BaseModel):
    store_name: str = Field(..., description="생성할 가게 이름", min_length=1, max_length=20)


class StoreUpdateRequest(BaseModel):
    store_name: str = Field(..., description="수정할 가게 이름", min_length=1, max_length=20)


class StoreResponse(BaseModel):
    store_id: str = Field(..., description="가게 고유 ID")
    store_name: str = Field(..., description="가게 이름")
    seller_email: str = Field(..., description="판매자 이메일")
    created_at: datetime = Field(..., description="가게 생성 시간")
    
    class Config:
        from_attributes = True


class StoreProductsResponse(BaseModel):
    store_id: str = Field(..., description="가게 고유 ID")
    store_name: str = Field(..., description="가게 이름")
    products: List[StoreProductResponse] = Field(default_factory=list, description="상품 목록")
    total: int = Field(..., description="전체 상품 수")


class StorePaymentInfoCreateRequest(BaseModel):
    portone_store_id: str = Field(..., description="포트원 가게 ID")
    portone_channel_id: str = Field(..., description="포트원 채널 ID")
    portone_secret_key: str = Field(..., description="포트원 시크릿 키")


class StorePaymentInfoResponse(BaseModel):
    store_id: str = Field(..., description="가게 고유 ID")
    portone_store_id: Optional[str] = Field(None, description="포트원 가게 ID")
    portone_channel_id: Optional[str] = Field(None, description="포트원 채널 ID")
    
    class Config:
        from_attributes = True


class StorePaymentInfoStatusResponse(BaseModel):
    info_status: bool = Field(..., description="결제 정보 등록 여부")