from typing import Optional
from pydantic import BaseModel, Field, field_validator


class ProductInfo(BaseModel):
    product_id:str = Field(..., description="상품 고유 ID")
    product_name:str = Field(..., description="상품 이름")
    stock:int = Field(..., description="상품 개수")
    price:int = Field(..., description="상품 가격")
    

class ProductsResponse(BaseModel):
    """결제 초기화 Response 스키마"""
    store_id: str = Field(..., description="가게 고유 ID")
    store_name: str = Field(..., description="가게 이름")
    products: list[ProductInfo] = Field(default_factory=list, description="상품 정보")


class ProductCreateRequest(BaseModel):
    """상품 생성 요청 스키마"""
    store_id: str = Field(..., description="가게 고유 ID")
    product_name: str = Field(..., description="상품 이름", min_length=1, max_length=255)
    initial_stock: int = Field(..., description="초기 재고 수량", ge=0)
    price: int = Field(..., description="상품 가격 (원 단위)", gt=0)
    sale: Optional[int] = Field(None, description="세일 퍼센트 (0-100)", ge=0, le=100)


class ProductUpdateRequest(BaseModel):
    """상품 정보 수정 요청 스키마"""
    product_name: Optional[str] = Field(None, description="상품 이름", min_length=1, max_length=255)
    price: Optional[int] = Field(None, description="상품 가격 (원 단위)", gt=0)
    sale: Optional[int] = Field(None, description="세일 퍼센트 (0-100)", ge=0, le=100)


class ProductStockUpdateRequest(BaseModel):
    """상품 재고 수정 요청 스키마"""
    stock: int = Field(..., description="변경할 재고 수량", ge=0)


class ProductResponse(BaseModel):
    """상품 응답 스키마"""
    product_id: str = Field(..., description="상품 고유 ID")
    store_id: str = Field(..., description="가게 고유 ID")
    product_name: str = Field(..., description="상품 이름")
    initial_stock: int = Field(..., description="초기 재고 수량")
    current_stock: int = Field(..., description="현재 재고 수량")
    price: int = Field(..., description="상품 가격 (원 단위)")
    sale: Optional[int] = Field(None, description="세일 퍼센트")
    version: int = Field(..., description="버전 (낙관적 락)")
    
    class Config:
        from_attributes = True