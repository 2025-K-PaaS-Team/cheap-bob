"""payment-svc 의 internal API — backend 가 호출.

X-Internal-Token 헤더 인증. JWT 미들웨어 EXCLUDE_PREFIXES 에 의해 JWT 우회.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from dependency_injector.wiring import Provide, inject

from app.middleware.internal_token import require_internal_token
from app.domain.payment.service.store_payment_info import StorePaymentInfoService
from app.domain.payment.service.payment_gateway import PaymentGatewayService
from app.domain.payment.service.exception import (
    PaymentInfoIncompleteError,
    PaymentInfoMissingError,
    PaymentRefundError,
)
from app.domain.payment.dto.internal import (
    ExistsInfoResponse,
    HasCompleteInfoResponse,
    RefundRequest,
    StorePaymentInfoInternalResponse,
    StorePaymentRegisterRequest,
)


internal_router = APIRouter(
    # 최종 등록 경로 = /api/internal (집계기) + /payment = /api/internal/payment/...
    prefix="/payment",
    tags=["Internal/Payment"],
    dependencies=[Depends(require_internal_token)],
)


@internal_router.get(
    "/store-info/{store_id}",
    response_model=StorePaymentInfoInternalResponse,
)
@inject
async def get_store_payment_info(
    store_id: str,
    store_payment_info_service: StorePaymentInfoService = Depends(
        Provide["store_payment_info_service"],
    ),
):
    """완전한 결제 정보 (포트원 모든 필드 채워짐) 반환. 누락 시 404."""
    try:
        info = await store_payment_info_service.get_complete_by_store(store_id)
    except (PaymentInfoMissingError, PaymentInfoIncompleteError) as e:
        raise HTTPException(status_code=404, detail=str(e))
    return StorePaymentInfoInternalResponse(
        store_id=info.store_id,
        portone_store_id=info.portone_store_id,
        portone_channel_id=info.portone_channel_id,
        portone_secret_key=info.portone_secret_key,
    )


@internal_router.get(
    "/store-info/{store_id}/has-complete",
    response_model=HasCompleteInfoResponse,
)
@inject
async def has_complete_info(
    store_id: str,
    store_payment_info_service: StorePaymentInfoService = Depends(
        Provide["store_payment_info_service"],
    ),
):
    """결제 정보가 완전한지 boolean. 없거나 불완전이어도 200 으로 false 반환."""
    has = await store_payment_info_service.has_complete_info(store_id)
    return HasCompleteInfoResponse(has_complete=has)


@internal_router.get(
    "/store-info/{store_id}/exists",
    response_model=ExistsInfoResponse,
)
@inject
async def exists_info(
    store_id: str,
    store_payment_info_service: StorePaymentInfoService = Depends(
        Provide["store_payment_info_service"],
    ),
):
    """결제 정보 row 가 존재하는지 (완전성 무관). 1차 가입 흐름의 register 충돌 회피용."""
    exists = await store_payment_info_service.exists_by_store(store_id)
    return ExistsInfoResponse(exists=exists)


@internal_router.delete(
    "/store-info/{store_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
@inject
async def delete_store_payment_info(
    store_id: str,
    store_payment_info_service: StorePaymentInfoService = Depends(
        Provide["store_payment_info_service"],
    ),
):
    """seller 탈퇴 cleanup. 없으면 204 (멱등)."""
    await store_payment_info_service.delete_by_store(store_id)


@internal_router.post(
    "/store-info",
    status_code=status.HTTP_204_NO_CONTENT,
)
@inject
async def register_store_payment_info(
    request: StorePaymentRegisterRequest,
    store_payment_info_service: StorePaymentInfoService = Depends(
        Provide["store_payment_info_service"],
    ),
):
    """가게 1차 등록 — 결제 정보 INSERT. 이미 있으면 409 (멱등 아님 — caller 책임)."""
    await store_payment_info_service.register(
        store_id=request.store_id,
        portone_store_id=request.portone_store_id,
        portone_channel_id=request.portone_channel_id,
        portone_secret_key=request.portone_secret_key,
    )


@internal_router.post(
    "/refund",
    status_code=status.HTTP_204_NO_CONTENT,
)
@inject
async def refund(
    request: RefundRequest,
    store_payment_info_service: StorePaymentInfoService = Depends(
        Provide["store_payment_info_service"],
    ),
    payment_gateway_service: PaymentGatewayService = Depends(
        Provide["payment_gateway_service"],
    ),
):
    """order cancel / store close 트리거. payment_id 별로 PortOne refund.

    payment-svc 가 secret_key 를 갖고 있어 caller (backend) 는 store_id 만 전달.
    환불 실패는 500 raise — caller 가 critical 로깅 후 운영자 알림.
    """
    try:
        info = await store_payment_info_service.get_complete_by_store(request.store_id)
    except (PaymentInfoMissingError, PaymentInfoIncompleteError) as e:
        raise HTTPException(status_code=400, detail=str(e))

    try:
        await payment_gateway_service.refund(
            payment_id=request.payment_id,
            secret_key=info.portone_secret_key,
            reason=request.reason,
        )
    except PaymentRefundError as e:
        raise HTTPException(status_code=500, detail=str(e))
