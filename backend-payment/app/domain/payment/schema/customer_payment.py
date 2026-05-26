from typing import Optional
from pydantic import BaseModel, Field


class PaymentInitRequest(BaseModel):
    """결제 초기화 요청 — 상품 + 수량."""
    product_id: str = Field(..., description="상품 고유 ID")
    quantity: int = Field(..., description="구매 수량")


class PaymentInitResponse(BaseModel):
    """결제 초기화 응답 — 프론트가 PortOne SDK 호출에 사용."""
    payment_id: str = Field(..., description="결제 고유 ID")
    channel_id: str = Field(..., description="포트원 채널 ID")
    store_id: str = Field(..., description="포트원 가게 ID")
    quantity: int = Field(..., description="구매 수량")
    price: int = Field(..., description="원가 (원)")
    sale: Optional[int] = Field(None, description="세일 퍼센트")
    total_amount: int = Field(..., description="최종 결제 금액")


class PaymentConfirmRequest(BaseModel):
    payment_id: str = Field(..., description="결제 고유 ID")


class PaymentResponse(BaseModel):
    payment_id: str = Field(..., description="결제 고유 ID")
