"""seller 의 결제 설정. payment-svc 가 직접 노출 — frontend → payment-svc 직접 호출.

store_id 는 backend 내부 (seller_email→store_id 매핑) 를 internal API 로 조회한다.
"""
from fastapi import APIRouter, Depends, status
from dependency_injector.wiring import Provide, inject

from app.middleware.auth import CurrentSellerDep
from app.domain.payment.service.seller_payment_settings import (
    SellerPaymentSettingsService,
)
from app.domain.payment.schema.store_payment_settings import (
    StoreInitPaymentResponse,
    StorePaymentResponse,
    StorePaymentSecretUpdateRequest,
    StorePaymentUpdateRequest,
)
from app.core.internal_client.seller import InternalSellerClient
from app.core.openapi import create_error_responses


router = APIRouter(prefix="/seller/store/settings", tags=["Seller-Store-Settings-Payment"])


async def _current_seller_store_id(current_user: CurrentSellerDep) -> str:
    """seller_email → store_id — backend internal API 로 조회.

    backend 의 seller_store_read_service.get_store_id_by_seller_email 와 동일.
    DI 가 어색하므로 직접 모듈 진입점에서 client 를 만든다 (singleton).
    """
    from app.container import container
    return await container.internal_seller_client().get_store_id_by_seller_email(
        current_user["sub"],
    )


@router.get(
    "/payment",
    response_model=StoreInitPaymentResponse,
    responses=create_error_responses({
        401: ["인증 정보가 없음", "토큰 만료"],
        404: "가게를 찾을 수 없음",
        502: "backend 일시 장애",
    }),
)
@inject
async def get_store_payment(
    store_id: str = Depends(_current_seller_store_id),
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
        502: "backend 일시 장애",
    }),
)
@inject
async def update_store_payment(
    request: StorePaymentUpdateRequest,
    store_id: str = Depends(_current_seller_store_id),
    settings_service: SellerPaymentSettingsService = Depends(
        Provide["seller_payment_settings_service"],
    ),
):
    """결제 정보 수정 (포트원 ID 만)."""
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
        502: "backend 일시 장애",
    }),
)
@inject
async def rotate_store_payment_secret(
    request: StorePaymentSecretUpdateRequest,
    store_id: str = Depends(_current_seller_store_id),
    settings_service: SellerPaymentSettingsService = Depends(
        Provide["seller_payment_settings_service"],
    ),
):
    """PortOne 콘솔 secret rotate 시 갱신."""
    await settings_service.rotate_secret_key(
        store_id=store_id, portone_secret_key=request.portone_secret_key,
    )
