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