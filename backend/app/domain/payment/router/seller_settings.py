from fastapi import APIRouter, Depends, status
from dependency_injector.wiring import Provide, inject

from app.domain.seller.router.deps import CurrentSellerStoreIdDep
from app.domain.payment.service.seller_payment_settings import (
    SellerPaymentSettingsService,
)
from app.domain.payment.schema.store_payment_settings import (
    StoreInitPaymentResponse,
    StorePaymentResponse,
    StorePaymentSecretUpdateRequest,
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
    store_id: CurrentSellerStoreIdDep,
    settings_service: SellerPaymentSettingsService = Depends(
        Provide["seller_payment_settings_service"],
    ),
):
    """결제 정보 조회 (포트원 ID, secret_key 미노출)."""
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
    store_id: CurrentSellerStoreIdDep,
    settings_service: SellerPaymentSettingsService = Depends(
        Provide["seller_payment_settings_service"],
    ),
):
    """결제 정보 수정 (포트원 ID 만, secret_key 는 별도 흐름)."""
    return await settings_service.update_ids(
        store_id=store_id,
        portone_store_id=request.portone_store_id,
        portone_channel_id=request.portone_channel_id,
    )


@router.put(
    "/payment/secret",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=create_error_responses({
        401: ["인증 정보가 없음", "토큰 만료"],
        404: "가게를 찾을 수 없음",
    }),
)
@inject
async def rotate_store_payment_secret(
    request: StorePaymentSecretUpdateRequest,
    store_id: CurrentSellerStoreIdDep,
    settings_service: SellerPaymentSettingsService = Depends(
        Provide["seller_payment_settings_service"],
    ),
):
    """PortOne 콘솔에서 시크릿 키를 rotate 한 경우 갱신. 응답에는 secret 미노출."""
    await settings_service.rotate_secret_key(
        store_id=store_id, portone_secret_key=request.portone_secret_key,
    )
