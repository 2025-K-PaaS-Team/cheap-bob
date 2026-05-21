from fastapi import APIRouter, Depends, HTTPException, status
from dependency_injector.wiring import Provide, inject

from app.middleware.auth import CurrentSellerDep, CurrentSellerNoActiveDep
from app.domain.seller.service.seller_store_read import SellerStoreReadService
from app.domain.seller.service.seller_store_profile import SellerStoreProfileService
from app.domain.seller.service.exception import StoreNotFoundError
from app.domain.seller.schema.seller_profile import (
    StoreIntroductionUpdateRequest,
    StoreNameUpdateRequest,
    StorePhoneUpdateRequest,
    StoreProfileResponse,
)
from app.domain.auth.schema.me import UserProfileMeResponse
from app.core.openapi import create_error_responses


router = APIRouter(prefix="/store/profile", tags=["Seller-Store-Profile"])


def _to_profile(store) -> StoreProfileResponse:
    return StoreProfileResponse(
        store_id=store.store_id,
        store_name=store.store_name,
        store_introduction=store.store_introduction,
        store_phone=store.store_phone,
    )


@router.get(
    "/me",
    response_model=UserProfileMeResponse,
    responses=create_error_responses({401: ["인증 정보가 없음", "토큰 만료"]}),
)
async def get_seller_me(current_user: CurrentSellerNoActiveDep):
    return UserProfileMeResponse(email=current_user["sub"])


@router.put(
    "/name",
    response_model=StoreProfileResponse,
    responses=create_error_responses({
        401: ["인증 정보가 없음", "토큰 만료"],
        404: "가게를 찾을 수 없음",
    }),
)
@inject
async def update_store_name(
    request: StoreNameUpdateRequest,
    current_user: CurrentSellerDep,
    store_read_service: SellerStoreReadService = Depends(
        Provide["seller_store_read_service"],
    ),
    profile_service: SellerStoreProfileService = Depends(
        Provide["seller_store_profile_service"],
    ),
):
    try:
        store_id = await store_read_service.get_store_id_by_seller_email(
            current_user["sub"],
        )
        store = await profile_service.update_name(store_id, request.store_name)
    except StoreNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return _to_profile(store)


@router.put(
    "/introduction",
    response_model=StoreProfileResponse,
    responses=create_error_responses({
        401: ["인증 정보가 없음", "토큰 만료"],
        404: "가게를 찾을 수 없음",
    }),
)
@inject
async def update_store_introduction(
    request: StoreIntroductionUpdateRequest,
    current_user: CurrentSellerDep,
    store_read_service: SellerStoreReadService = Depends(
        Provide["seller_store_read_service"],
    ),
    profile_service: SellerStoreProfileService = Depends(
        Provide["seller_store_profile_service"],
    ),
):
    try:
        store_id = await store_read_service.get_store_id_by_seller_email(
            current_user["sub"],
        )
        store = await profile_service.update_introduction(
            store_id, request.store_introduction,
        )
    except StoreNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return _to_profile(store)


@router.put(
    "/phone",
    response_model=StoreProfileResponse,
    responses=create_error_responses({
        401: ["인증 정보가 없음", "토큰 만료"],
        404: "가게를 찾을 수 없음",
        422: "유효하지 않은 전화번호 형식",
    }),
)
@inject
async def update_store_phone(
    request: StorePhoneUpdateRequest,
    current_user: CurrentSellerDep,
    store_read_service: SellerStoreReadService = Depends(
        Provide["seller_store_read_service"],
    ),
    profile_service: SellerStoreProfileService = Depends(
        Provide["seller_store_profile_service"],
    ),
):
    try:
        store_id = await store_read_service.get_store_id_by_seller_email(
            current_user["sub"],
        )
        store = await profile_service.update_phone(store_id, request.store_phone)
    except StoreNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return _to_profile(store)
