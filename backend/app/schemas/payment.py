from pydantic import BaseModel, Field, field_validator

class PaymentInitRequest(BaseModel):
    """결제 초기화 Request 스키마"""
    product_id: str = Field(..., description="상품 고유 ID")
    quantity: int = Field(..., description="상품 개수")


class PaymentInitResponse(BaseModel):
    """결제 초기화 Response 스키마"""
    success: bool = Field(..., description="성공 유무")
    payment_id: str = Field(..., description="결제 고유 ID")
    channel_id: str = Field(..., description="채널 고유 ID")
    store_id: str = Field(..., description="가게 고유 ID")
    message: str = Field(..., description="이유")


class PaymentConfirmRequest(BaseModel):
    """결제 확인 Request 스키마"""
    payment_id: str = Field(..., description="결제 고유 ID")
    


class PaymentConfirmResponse(BaseModel):
    """결제 확인 Response 스키마"""
    success: bool = Field(..., description="성공 유무")
    payment_id: str = Field(..., description="결제 고유 ID")
    message: str = Field(..., description="이유")

class PaymentRefundRequest(BaseModel):
    """환불 Request 스키마"""
    payment_id: str = Field(..., description="결제 고유 ID")
    reason: str = Field(description="환불 이유")


class PaymentRefundResponse(BaseModel):
    """환불 Response 스키마"""
    success: bool = Field(..., description="성공 유무")
    payment_id: str
    refund_amount: int | None = None
    message: str = Field(..., description="이유")