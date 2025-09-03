from pydantic import BaseModel, Field, field_validator

class PaymentInitRequest(BaseModel):
    """결제 초기화 Request 스키마"""
    product_id: str = Field(..., description="상품 고유 ID")
    quantity: int = Field(..., description="상품 개수")


class PaymentInitResponse(BaseModel):
    """결제 초기화 Response 스키마"""
    payment_id: str = Field(..., description="결제 고유 ID")
    channel_id: str = Field(..., description="채널 고유 ID")
    store_id: str = Field(..., description="가게 고유 ID")
    total_amount: int = Field(..., description="총 결제 금액")


class PaymentConfirmRequest(BaseModel):
    """결제 확인 Request 스키마"""
    payment_id: str = Field(..., description="결제 고유 ID")
    


class PaymentResponse(BaseModel):
    """결제 확인 Response 스키마"""
    payment_id: str = Field(..., description="결제 고유 ID")