from fastapi import APIRouter, Depends, HTTPException, status
from dependency_injector.wiring import Provide, inject

from app.middleware.auth import CurrentCustomerDep
from app.domain.customer.service.exception import (
    PreferenceDuplicateError,
    PreferenceNotFoundError,
)
from app.domain.customer.service.customer_preference import CustomerPreferenceService
from app.domain.customer.schema.customer_preference import (
    AllergyCreateRequest,
    AllergyDeleteRequest,
    AllergyListResponse,
    NutritionTypeCreateRequest,
    NutritionTypeDeleteRequest,
    NutritionTypeListResponse,
    PreferredMenuCreateRequest,
    PreferredMenuDeleteRequest,
    PreferredMenuListResponse,
    ToppingTypeCreateRequest,
    ToppingTypeDeleteRequest,
    ToppingTypeListResponse,
)
from app.core.openapi import create_error_responses


router = APIRouter(prefix="/profile", tags=["Customer-Profile"])


# ───────── PreferredMenu ─────────


@router.get(
    "/preferred-menus",
    response_model=PreferredMenuListResponse,
    responses=create_error_responses({401: ["인증 정보가 없음", "토큰 만료"]}),
)
@inject
async def get_preferred_menus(
    current_user: CurrentCustomerDep,
    service: CustomerPreferenceService = Depends(Provide["customer_preference_service"]),
):
    items = await service.list_preferred_menus(current_user["sub"])
    return PreferredMenuListResponse(preferred_menus=items)


@router.post(
    "/preferred-menus",
    response_model=PreferredMenuListResponse,
    status_code=status.HTTP_201_CREATED,
    responses=create_error_responses({
        400: ["잘못된 입력 형식", "중복된 메뉴"],
        401: ["인증 정보가 없음", "토큰 만료"],
    }),
)
@inject
async def add_preferred_menus(
    current_user: CurrentCustomerDep,
    data: PreferredMenuCreateRequest,
    service: CustomerPreferenceService = Depends(Provide["customer_preference_service"]),
):
    try:
        items = await service.add_preferred_menus(current_user["sub"], data.menu_types)
    except PreferenceDuplicateError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"이미 등록된 메뉴가 있습니다: {', '.join(e.duplicates)}",
        )
    return PreferredMenuListResponse(preferred_menus=items)


@router.delete(
    "/preferred-menus",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=create_error_responses({
        401: ["인증 정보가 없음", "토큰 만료"],
        404: ["선호 메뉴를 찾을 수 없음"],
    }),
)
@inject
async def delete_preferred_menu(
    current_user: CurrentCustomerDep,
    data: PreferredMenuDeleteRequest,
    service: CustomerPreferenceService = Depends(Provide["customer_preference_service"]),
):
    try:
        await service.remove_preferred_menu(current_user["sub"], data.menu_type)
    except PreferenceNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


# ───────── NutritionType ─────────


@router.get(
    "/nutrition-types",
    response_model=NutritionTypeListResponse,
    responses=create_error_responses({401: ["인증 정보가 없음", "토큰 만료"]}),
)
@inject
async def get_nutrition_types(
    current_user: CurrentCustomerDep,
    service: CustomerPreferenceService = Depends(Provide["customer_preference_service"]),
):
    items = await service.list_nutrition_types(current_user["sub"])
    return NutritionTypeListResponse(nutrition_types=items)


@router.post(
    "/nutrition-types",
    response_model=NutritionTypeListResponse,
    status_code=status.HTTP_201_CREATED,
    responses=create_error_responses({
        400: ["잘못된 입력 형식", "중복된 영양 타입"],
        401: ["인증 정보가 없음", "토큰 만료"],
    }),
)
@inject
async def add_nutrition_types(
    current_user: CurrentCustomerDep,
    data: NutritionTypeCreateRequest,
    service: CustomerPreferenceService = Depends(Provide["customer_preference_service"]),
):
    try:
        items = await service.add_nutrition_types(
            current_user["sub"], data.nutrition_types,
        )
    except PreferenceDuplicateError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"이미 등록된 영양 타입이 있습니다: {', '.join(e.duplicates)}",
        )
    return NutritionTypeListResponse(nutrition_types=items)


@router.delete(
    "/nutrition-types",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=create_error_responses({
        401: ["인증 정보가 없음", "토큰 만료"],
        404: ["영양 타입을 찾을 수 없음"],
    }),
)
@inject
async def delete_nutrition_type(
    current_user: CurrentCustomerDep,
    data: NutritionTypeDeleteRequest,
    service: CustomerPreferenceService = Depends(Provide["customer_preference_service"]),
):
    try:
        await service.remove_nutrition_type(current_user["sub"], data.nutrition_type)
    except PreferenceNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


# ───────── Allergy ─────────


@router.get(
    "/allergies",
    response_model=AllergyListResponse,
    responses=create_error_responses({401: ["인증 정보가 없음", "토큰 만료"]}),
)
@inject
async def get_allergies(
    current_user: CurrentCustomerDep,
    service: CustomerPreferenceService = Depends(Provide["customer_preference_service"]),
):
    items = await service.list_allergies(current_user["sub"])
    return AllergyListResponse(allergies=items)


@router.post(
    "/allergies",
    response_model=AllergyListResponse,
    status_code=status.HTTP_201_CREATED,
    responses=create_error_responses({
        400: ["잘못된 입력 형식", "중복된 알레르기"],
        401: ["인증 정보가 없음", "토큰 만료"],
    }),
)
@inject
async def add_allergies(
    current_user: CurrentCustomerDep,
    data: AllergyCreateRequest,
    service: CustomerPreferenceService = Depends(Provide["customer_preference_service"]),
):
    try:
        items = await service.add_allergies(current_user["sub"], data.allergy_types)
    except PreferenceDuplicateError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"이미 등록된 알레르기가 있습니다: {', '.join(e.duplicates)}",
        )
    return AllergyListResponse(allergies=items)


@router.delete(
    "/allergies",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=create_error_responses({
        401: ["인증 정보가 없음", "토큰 만료"],
        404: ["알레르기를 찾을 수 없음"],
    }),
)
@inject
async def delete_allergy(
    current_user: CurrentCustomerDep,
    data: AllergyDeleteRequest,
    service: CustomerPreferenceService = Depends(Provide["customer_preference_service"]),
):
    try:
        await service.remove_allergy(current_user["sub"], data.allergy_type)
    except PreferenceNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


# ───────── ToppingType ─────────


@router.get(
    "/topping-types",
    response_model=ToppingTypeListResponse,
    responses=create_error_responses({401: ["인증 정보가 없음", "토큰 만료"]}),
)
@inject
async def get_topping_types(
    current_user: CurrentCustomerDep,
    service: CustomerPreferenceService = Depends(Provide["customer_preference_service"]),
):
    items = await service.list_topping_types(current_user["sub"])
    return ToppingTypeListResponse(topping_types=items)


@router.post(
    "/topping-types",
    response_model=ToppingTypeListResponse,
    status_code=status.HTTP_201_CREATED,
    responses=create_error_responses({
        400: ["잘못된 입력 형식", "중복된 토핑 타입"],
        401: ["인증 정보가 없음", "토큰 만료"],
    }),
)
@inject
async def add_topping_types(
    current_user: CurrentCustomerDep,
    data: ToppingTypeCreateRequest,
    service: CustomerPreferenceService = Depends(Provide["customer_preference_service"]),
):
    try:
        items = await service.add_topping_types(current_user["sub"], data.topping_types)
    except PreferenceDuplicateError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"이미 등록된 토핑 타입이 있습니다: {', '.join(e.duplicates)}",
        )
    return ToppingTypeListResponse(topping_types=items)


@router.delete(
    "/topping-types",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=create_error_responses({
        401: ["인증 정보가 없음", "토큰 만료"],
        404: ["토핑 타입을 찾을 수 없음"],
    }),
)
@inject
async def delete_topping_type(
    current_user: CurrentCustomerDep,
    data: ToppingTypeDeleteRequest,
    service: CustomerPreferenceService = Depends(Provide["customer_preference_service"]),
):
    try:
        await service.remove_topping_type(current_user["sub"], data.topping_type)
    except PreferenceNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
