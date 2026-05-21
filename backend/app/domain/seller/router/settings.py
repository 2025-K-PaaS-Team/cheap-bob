from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from dependency_injector.wiring import Provide, inject
from datetime import datetime

from app.middleware.auth import CurrentSellerDep
from app.domain.seller.service.seller_store_settings import SellerStoreSettingsService
from app.domain.seller.service.seller_store_read import SellerStoreReadService
from app.domain.seller.service.exception import (
    StoreNotFoundError,
    StoreOperationReservationNotFoundError,
)
from app.domain.seller.schema.store_settings import (
    StoreAddressResponse,
    StoreAddressUpdateRequest,
    StoreOperationModificationResponse,
    StoreOperationReservationRequest,
    StoreOperationReservationResponse,
    StoreOperationResponse,
)
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
    current_user: CurrentSellerDep,
    store_read_service: SellerStoreReadService = Depends(
        Provide["seller_store_read_service"],
    ),
    settings_service: SellerStoreSettingsService = Depends(
        Provide["seller_store_settings_service"],
    ),
):
    try:
        store_id = await store_read_service.get_store_id_by_seller_email(
            current_user["sub"],
        )
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
    except StoreNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

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
    response_model=List[StoreOperationResponse],
    responses=create_error_responses({
        401: ["인증 정보가 없음", "토큰 만료"],
        404: "가게를 찾을 수 없음",
    }),
)
@inject
async def get_store_operation(
    current_user: CurrentSellerDep,
    store_read_service: SellerStoreReadService = Depends(
        Provide["seller_store_read_service"],
    ),
    settings_service: SellerStoreSettingsService = Depends(
        Provide["seller_store_settings_service"],
    ),
):
    try:
        store_id = await store_read_service.get_store_id_by_seller_email(
            current_user["sub"],
        )
        infos = await settings_service.list_operation(store_id)
    except StoreNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    return [
        StoreOperationResponse(
            day_of_week=info.day_of_week,
            open_time=info.open_time,
            close_time=info.close_time,
            pickup_start_time=info.pickup_start_time,
            pickup_end_time=info.pickup_end_time,
            is_open_enabled=info.is_open_enabled,
        )
        for info in sorted(infos, key=lambda x: x.day_of_week)
    ]


# ───────── operation reservation ─────────


def _modification_type(modifications, operations) -> tuple[int, "int|None"]:
    """[helper] modifications vs operations 비교 → (modification_type, None)"""
    op_map = {info.operation_id: info for info in operations}
    has_time = False
    has_pickup = False
    for mod in modifications:
        origin = op_map.get(mod.operation_id)
        if origin is None:
            continue
        if (
            mod.new_open_time != origin.open_time
            or mod.new_close_time != origin.close_time
            or mod.new_is_open_enabled != origin.is_open_enabled
        ):
            has_time = True
        mod_pstart = datetime.combine(datetime.today(), mod.new_close_time) - datetime.combine(
            datetime.today(), mod.new_pickup_start_time,
        )
        orig_pstart = datetime.combine(datetime.today(), origin.close_time) - datetime.combine(
            datetime.today(), origin.pickup_start_time,
        )
        mod_pend = datetime.combine(datetime.today(), mod.new_close_time) - datetime.combine(
            datetime.today(), mod.new_pickup_end_time,
        )
        orig_pend = datetime.combine(datetime.today(), origin.close_time) - datetime.combine(
            datetime.today(), origin.pickup_end_time,
        )
        if (
            mod.new_is_open_enabled == origin.is_open_enabled
            and (mod_pstart != orig_pstart or mod_pend != orig_pend)
        ):
            has_pickup = True

    if has_time and has_pickup:
        return 3, None
    if has_pickup:
        return 2, None
    if has_time:
        return 1, None
    return 0, None


def _pickup_intervals(op_or_mod, *, is_modification: bool) -> tuple[int, int]:
    """오픈 가능한 첫 항목 기준 pickup 간격 (마감으로부터의 분)."""
    if op_or_mod is None:
        return 60, 30
    if is_modification:
        ps = op_or_mod.new_pickup_start_time
        pe = op_or_mod.new_pickup_end_time
        cl = op_or_mod.new_close_time
    else:
        ps = op_or_mod.pickup_start_time
        pe = op_or_mod.pickup_end_time
        cl = op_or_mod.close_time

    close_dt = datetime.combine(datetime.today(), cl)
    pickup_start = int((close_dt - datetime.combine(datetime.today(), ps)).total_seconds() // 60)
    pickup_end = int((close_dt - datetime.combine(datetime.today(), pe)).total_seconds() // 60)
    return pickup_start, pickup_end


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
    current_user: CurrentSellerDep,
    store_read_service: SellerStoreReadService = Depends(
        Provide["seller_store_read_service"],
    ),
    settings_service: SellerStoreSettingsService = Depends(
        Provide["seller_store_settings_service"],
    ),
):
    """현재 예약된 운영 변경 사항 + 변경 타입 + pickup 간격."""
    try:
        store_id = await store_read_service.get_store_id_by_seller_email(
            current_user["sub"],
        )
        modifications = await settings_service.list_operation_modifications(store_id)
        operations = await settings_service.list_operation(store_id)
    except StoreNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    if not modifications:
        # 예약 없음 → 현재 운영 정보를 그대로 매핑.
        responses = [
            StoreOperationModificationResponse(
                operation_id=info.operation_id,
                day_of_week=info.day_of_week,
                new_open_time=info.open_time,
                new_close_time=info.close_time,
                new_is_open_enabled=info.is_open_enabled,
                created_at=info.updated_at,
            )
            for info in sorted(operations, key=lambda x: x.day_of_week)
        ]
        open_op = next((o for o in operations if o.is_open_enabled), None)
        ps, pe = _pickup_intervals(open_op, is_modification=False)
        return StoreOperationReservationResponse(
            modification_type=0,
            modifications=responses,
            new_pickup_start_interval=ps,
            new_pickup_end_interval=pe,
        )

    mod_type, _ = _modification_type(modifications, operations)
    open_mod = next((m for m in modifications if m.new_is_open_enabled), None)
    ps, pe = _pickup_intervals(open_mod, is_modification=True)
    responses = [
        StoreOperationModificationResponse(
            operation_id=mod.operation_id,
            day_of_week=mod.operation_info.day_of_week,
            new_open_time=mod.new_open_time,
            new_close_time=mod.new_close_time,
            new_is_open_enabled=mod.new_is_open_enabled,
            created_at=mod.created_at,
        )
        for mod in sorted(modifications, key=lambda x: x.operation_info.day_of_week)
    ]
    return StoreOperationReservationResponse(
        modification_type=mod_type,
        modifications=responses,
        new_pickup_start_interval=ps,
        new_pickup_end_interval=pe,
    )


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
    current_user: CurrentSellerDep,
    store_read_service: SellerStoreReadService = Depends(
        Provide["seller_store_read_service"],
    ),
    settings_service: SellerStoreSettingsService = Depends(
        Provide["seller_store_settings_service"],
    ),
):
    """upsert — 기존 예약이 있으면 덮어쓰기."""
    try:
        store_id = await store_read_service.get_store_id_by_seller_email(
            current_user["sub"],
        )
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
    except StoreNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


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
    current_user: CurrentSellerDep,
    store_read_service: SellerStoreReadService = Depends(
        Provide["seller_store_read_service"],
    ),
    settings_service: SellerStoreSettingsService = Depends(
        Provide["seller_store_settings_service"],
    ),
):
    try:
        store_id = await store_read_service.get_store_id_by_seller_email(
            current_user["sub"],
        )
        await settings_service.delete_operation_modifications(store_id)
    except StoreNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except StoreOperationReservationNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
