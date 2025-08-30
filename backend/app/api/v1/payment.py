from typing import Dict
from fastapi import APIRouter, HTTPException, Path

from schemas.payment import (
    PaymentInitRequest,
    PaymentInitResponse,
    PaymentConfirmRequest,
    PaymentConfirmResponse,
    PaymentRefundRequest,
    PaymentRefundResponse
)

from services.payment import PaymentService

router = APIRouter(prefix="/payment", tags=["payment"])

@router.post("/init", response_model=PaymentInitResponse)
async def init_payment(request: PaymentInitRequest):
    """
    결제 초기화 API - 상품과 수량을 확인하고 결제 세션을 생성합니다.
    """
    # PaymentService를 통해 결제 세션 생성
    result = await PaymentService.create_payment_session(request.product_id, request.quantity)

    # 포트원 설정 정보 가져오기
    portone_config = result["portone_config"]
    
    return PaymentInitResponse(
        success= True,
        payment_id=result["payment_id"],
        channel_id=portone_config.get("portone_channel_id", ""),
        store_id=portone_config.get("portone_store_id", ""),
        message="정상 결제 가능"
    )


@router.post("/confirm", response_model=PaymentConfirmResponse)
async def confirm_payment(request: PaymentConfirmRequest):
    """
    결제 최종 확인 API - 포트원에서 결제가 성공했는지 확인하는 용도
    """
    # PaymentService를 통해 결제 검증
    result = await PaymentService.verify_payment(request.payment_id)
    
    payment_info = result["payment_info"]
    
    return PaymentConfirmResponse(
        success=True,
        payment_id=request.payment_id,
        message="정상 결제 확인 완료"
    )


@router.post("/refund", response_model=PaymentRefundResponse)
async def refund_payment(request: PaymentRefundRequest):
    """
    환불 테스트 API
    """
    # PaymentService를 통해 환불 처리
    result = await PaymentService.process_refund(
        payment_id=request.payment_id,
        reason=request.reason,
    )
    
    return PaymentRefundResponse(
        success=True,
        payment_id=request.payment_id,
        refund_amount=result['refund_amount'],
        message=f"환불이 완료되었습니다. 환불 금액: {result['refund_amount']:,}원"
    )