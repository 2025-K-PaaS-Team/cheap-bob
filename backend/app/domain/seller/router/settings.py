from typing import List
from fastapi import APIRouter, Depends, status
from dependency_injector.wiring import Provide, inject

from app.domain.seller.service.seller_store_settings import SellerStoreSettingsService
from app.domain.seller.schema.store_settings import (
    StoreAddressResponse,
    StoreAddressUpdateRequest,
    StoreDailyOperationResponse,
    StoreOperationReservationRequest,
    StoreOperationReservationResponse,
)
from app.domain.seller.router.deps import CurrentSellerStoreIdDep
from app.core.openapi import create_error_responses


router = APIRouter(prefix="/store/settings", tags=["Seller-Store-Settings"])


# ───────── address ─────────


@router.put(
    "/address",
    response_model=StoreAddressResponse,
    responses=create_error_responses({
        401: ["인증 정보가 없음", "토큰 만료"],
        404: "가게를 찾을 수 없음",
    }),
)
@inject
async def update_store_address(
    request: StoreAddressUpdateRequest,
    store_id: CurrentSellerStoreIdDep,
    settings_service: SellerStoreSettingsService = Depends(
        Provide["seller_store_settings_service"],
    ),
):
    await settings_service.update_address(
        store_id=store_id,
        postal_code=request.postal_code,
        address=request.address,
        detail_address=request.detail_address,
        sido=request.sido,
        sigungu=request.sigungu,
        bname=request.bname,
        lat=request.lat,
        lng=request.lng,
        nearest_station=request.nearest_station,
        walking_time=request.walking_time,
    )

    return StoreAddressResponse(
        store_id=store_id,
        postal_code=request.postal_code,
        address=request.address,
        detail_address=request.detail_address,
        sido=request.sido,
        sigungu=request.sigungu,
        bname=request.bname,
        lat=request.lat,
        lng=request.lng,
        nearest_station=request.nearest_station,
        walking_time=request.walking_time,
    )


# ───────── operation ─────────


@router.get(
    "/operation",
    response_model=List[StoreDailyOperationResponse],
    responses=create_error_responses({
        401: ["인증 정보가 없음", "토큰 만료"],
        404: "가게를 찾을 수 없음",
    }),
)
@inject
async def get_store_operation(
    store_id: CurrentSellerStoreIdDep,
    settings_service: SellerStoreSettingsService = Depends(
        Provide["seller_store_settings_service"],
    ),
):
    infos = await settings_service.list_operation(store_id)

    return [
        StoreDailyOperationResponse.model_validate(info)
        for info in sorted(infos, key=lambda x: x.day_of_week)
    ]


# ───────── operation reservation ─────────


@router.get(
    "/operation/reservation",
    response_model=StoreOperationReservationResponse,
    responses=create_error_responses({
        401: ["인증 정보가 없음", "토큰 만료"],
        404: "가게를 찾을 수 없음",
    }),
)
@inject
async def get_operation_reservation(
    store_id: CurrentSellerStoreIdDep,
    settings_service: SellerStoreSettingsService = Depends(
        Provide["seller_store_settings_service"],
    ),
):
    """현재 예약된 운영 변경 사항 + 변경 타입 + pickup 간격. 분류·간격 계산은 service 책임."""
    return await settings_service.get_operation_reservation_summary(store_id)


@router.post(
    "/operation/reservation",
    status_code=status.HTTP_201_CREATED,
    responses=create_error_responses({
        401: ["인증 정보가 없음", "토큰 만료"],
        404: "가게를 찾을 수 없음",
        400: ["이미 예약이 존재함", "시간 설정이 올바르지 않음"],
    }),
)
@inject
async def create_or_update_operation_reservation(
    request: StoreOperationReservationRequest,
    store_id: CurrentSellerStoreIdDep,
    settings_service: SellerStoreSettingsService = Depends(
        Provide["seller_store_settings_service"],
    ),
):
    """upsert — 기존 예약이 있으면 덮어쓰기."""
    await settings_service.upsert_operation_modifications(
        store_id=store_id,
        modifications=[
            {
                "day_of_week": op.day_of_week,
                "open_time": op.open_time,
                "close_time": op.close_time,
                "pickup_start_time": op.pickup_start_time,
                "pickup_end_time": op.pickup_end_time,
                "is_open_enabled": op.is_open_enabled,
            }
            for op in request.operation_times
        ],
    )


@router.delete(
    "/operation/reservation",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=create_error_responses({
        401: ["인증 정보가 없음", "토큰 만료"],
        404: ["가게를 찾을 수 없음", "예약을 찾을 수 없음"],
    }),
)
@inject
async def delete_operation_reservation(
    store_id: CurrentSellerStoreIdDep,
    settings_service: SellerStoreSettingsService = Depends(
        Provide["seller_store_settings_service"],
    ),
):
    await settings_service.delete_operation_modifications(store_id)
