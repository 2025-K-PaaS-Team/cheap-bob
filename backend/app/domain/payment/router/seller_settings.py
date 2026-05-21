from fastapi import APIRouter, Depends, HTTPException, status
from dependency_injector.wiring import Provide, inject

from app.middleware.auth import CurrentSellerDep
from app.domain.seller.service.seller_store_read import SellerStoreReadService
from app.domain.seller.service.exception import StoreNotFoundError
from app.domain.payment.service.seller_payment_settings import (
    SellerPaymentSettingsService,
)
from app.domain.payment.schema.store_payment_settings import (
    StoreInitPaymentResponse,
    StorePaymentResponse,
    StorePaymentUpdateRequest,
)
from app.core.openapi import create_error_responses


router = APIRouter(prefix="/seller/store/settings", tags=["Seller-Store-Settings-Payment"])


@router.get(
    "/payment",
    response_model=StoreInitPaymentResponse,
    responses=create_error_responses({
        401: ["인증 정보가 없음", "토큰 만료"],
        404: "가게를 찾을 수 없음",
    }),
)
@inject
async def get_store_payment(
    current_user: CurrentSellerDep,
    seller_store_read_service: SellerStoreReadService = Depends(
        Provide["seller_store_read_service"],
    ),
    settings_service: SellerPaymentSettingsService = Depends(
        Provide["seller_payment_settings_service"],
    ),
):
    """결제 정보 조회 (포트원 ID, secret_key 미노출)."""
    try:
        store_id = await seller_store_read_service.get_store_id_by_seller_email(
            current_user["sub"],
        )
    except StoreNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return await settings_service.get_initial(store_id)


@router.put(
    "/payment",
    response_model=StorePaymentResponse,
    responses=create_error_responses({
        401: ["인증 정보가 없음", "토큰 만료"],
        404: "가게를 찾을 수 없음",
    }),
)
@inject
async def update_store_payment(
    request: StorePaymentUpdateRequest,
    current_user: CurrentSellerDep,
    seller_store_read_service: SellerStoreReadService = Depends(
        Provide["seller_store_read_service"],
    ),
    settings_service: SellerPaymentSettingsService = Depends(
        Provide["seller_payment_settings_service"],
    ),
):
    """결제 정보 수정 (포트원 ID 만, secret_key 는 별도 흐름)."""
    try:
        store_id = await seller_store_read_service.get_store_id_by_seller_email(
            current_user["sub"],
        )
    except StoreNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return await settings_service.update_ids(
        store_id=store_id,
        portone_store_id=request.portone_store_id,
        portone_channel_id=request.portone_channel_id,
    )
