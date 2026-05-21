from fastapi import APIRouter, Depends, HTTPException, status
from dependency_injector.wiring import Provide, inject

from app.middleware.auth import CurrentCustomerDep
from app.domain.customer.service.exception import CustomerAlreadyRegisteredError
from app.domain.customer.service.customer_register import CustomerRegisterService
from app.domain.customer.schema.customer_register import CustomerRegisterRequest
from app.domain.customer.schema.customer_profile import CustomerProfileResponse
from app.domain.customer.dto.profile import CustomerFullProfile
from app.core.openapi import create_error_responses


router = APIRouter(prefix="/register", tags=["Customer-Register"])


@router.post(
    "",
    response_model=CustomerProfileResponse,
    status_code=status.HTTP_201_CREATED,
    responses=create_error_responses({
        400: ["이미 프로필이 존재함", "잘못된 입력 형식"],
        401: ["인증 정보가 없음", "토큰 만료"],
    }),
)
@inject
async def customer_register(
    current_user: CurrentCustomerDep,
    register_data: CustomerRegisterRequest,
    register_service: CustomerRegisterService = Depends(
        Provide["customer_register_service"],
    ),
):
    """소비자 통합 회원가입 — 상세정보, 선호메뉴, 영양타입, 알레르기, 토핑타입을 한 트랜잭션에 등록."""
    try:
        detail, menus, nutrition, allergies, toppings = await register_service.register(
            customer_email=current_user["sub"],
            nickname=register_data.nickname,
            phone_number=register_data.phone_number,
            preferred_menus=register_data.preferred_menus,
            nutrition_types=register_data.nutrition_types,
            allergies=register_data.allergies,
            topping_types=register_data.topping_types,
        )
    except CustomerAlreadyRegisteredError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    return CustomerProfileResponse.model_validate(
        CustomerFullProfile(
            detail=detail,
            preferred_menus=menus,
            nutrition_types=nutrition,
            allergies=allergies,
            topping_types=toppings,
        ),
    )
