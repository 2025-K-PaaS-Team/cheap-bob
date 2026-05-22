from typing import List
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from dependency_injector.wiring import Provide, inject

from app.util.image_validator import validate_image_files
from app.middleware.auth import CurrentSellerDep
from app.domain.seller.service.seller_store_register import SellerStoreRegisterService
from app.domain.seller.service.seller_store_image import SellerStoreImageService
from app.domain.seller.schema.seller_profile import (
    SellerProfileCreateRequest,
    SellerProfileResponse,
)
from app.domain.seller.schema.image import StoreImagesUploadResponse
from app.domain.seller.router.deps import CurrentSellerStoreIdDep
from app.domain.payment.service.seller_payment_settings import (
    SellerPaymentSettingsService,
)
from app.domain.payment.schema.store_payment_settings import (
    StorePaymentInfoCheckResponse,
    StorePaymentInfoCreateRequest,
)
from app.core.openapi import create_error_responses


router = APIRouter(prefix="/store/register", tags=["Seller-Store-Register"])

_MAX_IMAGES = 11


@router.post(
    "",
    response_model=SellerProfileResponse,
    status_code=status.HTTP_201_CREATED,
    responses=create_error_responses({
        401: ["인증 정보가 없음", "토큰 만료"],
        409: ["이미 가게가 등록된 판매자"],
    }),
)
@inject
async def register_seller_store(
    request: SellerProfileCreateRequest,
    current_user: CurrentSellerDep,
    register_service: SellerStoreRegisterService = Depends(
        Provide["seller_store_register_service"],
    ),
):
    """판매자 1차 가게 등록 — store + address + sns + operation 한 트랜잭션 생성."""
    sns_info = None
    if request.sns_info:
        sns_info = {
            "instagram": str(request.sns_info.instagram) if request.sns_info.instagram else None,
            "facebook": str(request.sns_info.facebook) if request.sns_info.facebook else None,
            "x": str(request.sns_info.x) if request.sns_info.x else None,
            "homepage": str(request.sns_info.homepage) if request.sns_info.homepage else None,
        }
    operation_times = [
        {
            "day_of_week": op.day_of_week,
            "open_time": op.open_time,
            "close_time": op.close_time,
            "pickup_start_time": op.pickup_start_time,
            "pickup_end_time": op.pickup_end_time,
            "is_open_enabled": op.is_open_enabled,
        }
        for op in request.operation_times
    ]

    store = await register_service.register(
        seller_email=current_user["sub"],
        store_name=request.store_name,
        store_introduction=request.store_introduction,
        store_phone=request.store_phone,
        store_postal_code=request.address_info.postal_code,
        store_address=request.address_info.address,
        store_detail_address=request.address_info.detail_address,
        sido=request.address_info.sido,
        sigungu=request.address_info.sigungu,
        bname=request.address_info.bname,
        lat=request.address_info.lat,
        lng=request.address_info.lng,
        nearest_station=request.address_info.nearest_station,
        walking_time=request.address_info.walking_time,
        sns_info=sns_info,
        operation_times=operation_times,
    )

    return SellerProfileResponse(store_id=store.store_id, store_name=store.store_name)


@router.post(
    "/images",
    response_model=StoreImagesUploadResponse,
    status_code=status.HTTP_201_CREATED,
    responses=create_error_responses({
        400: ["업로드할 이미지가 없음", f"이미지는 최대 {_MAX_IMAGES}개", "지원하지 않는 파일 형식"],
        401: ["인증 정보가 없음", "토큰 만료"],
        404: "가게를 찾을 수 없음",
        409: "이미 등록된 이미지가 있음",
        413: "파일 크기가 너무 큼",
    }),
)
@inject
async def register_store_images(
    current_user: CurrentSellerDep,
    store_id: CurrentSellerStoreIdDep,
    files: List[UploadFile] = File(..., description="첫 번째가 대표 이미지. 최대 11개 / 15MB / jpeg/png/webp"),
    image_service: SellerStoreImageService = Depends(
        Provide["seller_store_image_service"],
    ),
):
    """가게 이미지 최초 등록 — 첫 번째 파일이 대표 이미지."""
    seller_email = current_user["sub"]
    if not files:
        raise HTTPException(status_code=400, detail="업로드할 이미지가 없습니다.")
    if len(files) > _MAX_IMAGES:
        raise HTTPException(
            status_code=400, detail=f"이미지는 최대 {_MAX_IMAGES}개까지 업로드 가능합니다.",
        )

    try:
        validated = await validate_image_files(files)
        return await image_service.init_images(
            store_id=store_id, seller_email=seller_email, files=validated,
        )
    finally:
        for f in files:
            await f.close()


@router.post(
    "/payment",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=create_error_responses({
        401: ["인증 정보가 없음", "토큰 만료"],
        404: "가게를 찾을 수 없음",
        409: "이미 결제 정보가 등록되어 있음",
    }),
)
@inject
async def register_payment_info(
    request: StorePaymentInfoCreateRequest,
    store_id: CurrentSellerStoreIdDep,
    payment_settings_service: SellerPaymentSettingsService = Depends(
        Provide["seller_payment_settings_service"],
    ),
):
    """가게 1차 가입의 결제 정보 등록 — payment 도메인의 service 에 위임."""
    await payment_settings_service.register(
        store_id=store_id,
        portone_store_id=request.portone_store_id,
        portone_channel_id=request.portone_channel_id,
        portone_secret_key=request.portone_secret_key,
    )


@router.get(
    "/payment",
    response_model=StorePaymentInfoCheckResponse,
    responses=create_error_responses({
        401: ["인증 정보가 없음", "토큰 만료"],
        404: "가게를 찾을 수 없음",
    }),
)
@inject
async def check_payment_info(
    store_id: CurrentSellerStoreIdDep,
    payment_settings_service: SellerPaymentSettingsService = Depends(
        Provide["seller_payment_settings_service"],
    ),
):
    """결제 정보 등록 여부 확인."""
    exists = await payment_settings_service.exists(store_id)
    return StorePaymentInfoCheckResponse(is_exist=exists)
