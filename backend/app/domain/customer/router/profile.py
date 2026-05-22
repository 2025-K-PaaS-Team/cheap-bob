from fastapi import APIRouter, Depends, HTTPException, status
from dependency_injector.wiring import Provide, inject

from app.middleware.auth import CurrentCustomerDep, CurrentCustomerNoActiveDep
from app.domain.customer.service.customer_profile import CustomerProfileService
from app.domain.customer.service.customer_detail import CustomerDetailService
from app.domain.customer.schema.customer_profile import CustomerProfileResponse
from app.domain.customer.schema.customer_detail import (
    CustomerDetailResponse,
    CustomerDetailUpdateRequest,
)
from app.domain.auth.schema.me import UserProfileMeResponse
from app.core.openapi import create_error_responses


router = APIRouter(prefix="/profile", tags=["Customer-Profile"])


@router.get(
    "",
    response_model=CustomerProfileResponse,
    responses=create_error_responses({
        401: ["인증 정보가 없음", "토큰 만료"],
        404: ["소비자 상세 정보가 없음"],
    }),
)
@inject
async def get_customer_profile(
    current_user: CurrentCustomerDep,
    profile_service: CustomerProfileService = Depends(
        Provide["customer_profile_service"],
    ),
):
    """소비자의 detail + 4종 선호 통합 응답."""
    profile = await profile_service.get_full_profile(current_user["sub"])
    return CustomerProfileResponse.model_validate(profile)


@router.get(
    "/me",
    response_model=UserProfileMeResponse,
    responses=create_error_responses({401: ["인증 정보가 없음", "토큰 만료"]}),
)
async def get_customer_me(current_user: CurrentCustomerNoActiveDep):
    """현재 로그인 사용자의 이메일."""
    return UserProfileMeResponse(email=current_user["sub"])


@router.get(
    "/detail",
    response_model=CustomerDetailResponse,
    responses=create_error_responses({
        401: ["인증 정보가 없음", "토큰 만료"],
        404: ["소비자 상세 정보가 없음"],
    }),
)
@inject
async def get_customer_detail(
    current_user: CurrentCustomerDep,
    detail_service: CustomerDetailService = Depends(
        Provide["customer_detail_service"],
    ),
):
    return await detail_service.get(current_user["sub"])


@router.patch(
    "/detail",
    response_model=CustomerDetailResponse,
    responses=create_error_responses({
        400: ["수정할 정보가 없음", "잘못된 입력 형식"],
        401: ["인증 정보가 없음", "토큰 만료"],
        404: ["소비자 상세 정보가 없음"],
    }),
)
@inject
async def update_customer_detail(
    current_user: CurrentCustomerDep,
    detail_data: CustomerDetailUpdateRequest,
    detail_service: CustomerDetailService = Depends(
        Provide["customer_detail_service"],
    ),
):
    update_dict = detail_data.model_dump(exclude_unset=True)
    if not update_dict:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="수정할 정보가 없습니다",
        )

    return await detail_service.update(
        customer_email=current_user["sub"],
        nickname=update_dict.get("nickname"),
        phone_number=update_dict.get("phone_number"),
    )
