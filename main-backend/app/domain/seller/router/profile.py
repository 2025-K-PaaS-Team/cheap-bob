from fastapi import APIRouter, Depends
from dependency_injector.wiring import Provide, inject

from app.middleware.auth import CurrentSellerNoActiveDep
from app.domain.seller.service.seller_store_profile import SellerStoreProfileService
from app.domain.seller.schema.seller_profile import (
    StoreIntroductionUpdateRequest,
    StoreNameUpdateRequest,
    StorePhoneUpdateRequest,
    StoreProfileResponse,
)
from app.domain.seller.router.deps import CurrentSellerStoreIdDep
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
    store_id: CurrentSellerStoreIdDep,
    profile_service: SellerStoreProfileService = Depends(
        Provide["seller_store_profile_service"],
    ),
):
    store = await profile_service.update_name(store_id, request.store_name)
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
    store_id: CurrentSellerStoreIdDep,
    profile_service: SellerStoreProfileService = Depends(
        Provide["seller_store_profile_service"],
    ),
):
    store = await profile_service.update_introduction(
        store_id, request.store_introduction,
    )
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
    store_id: CurrentSellerStoreIdDep,
    profile_service: SellerStoreProfileService = Depends(
        Provide["seller_store_profile_service"],
    ),
):
    store = await profile_service.update_phone(store_id, request.store_phone)
    return _to_profile(store)
