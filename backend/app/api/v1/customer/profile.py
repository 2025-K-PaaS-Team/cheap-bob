from fastapi import APIRouter, HTTPException, status

from utils.docs_error import create_error_responses
from api.deps.auth import CurrentCustomerDep
from api.deps.repository import (
    CustomerDetailRepositoryDep,
    CustomerPreferredMenuRepositoryDep,
    CustomerNutritionTypeRepositoryDep,
    CustomerAllergyRepositoryDep,
    CustomerToppingTypeRepositoryDep,
    CustomerProfileRepositoryDep
)
from schemas.customer_detail import (
    CustomerDetailResponse,
    CustomerDetailUpdate
)
from schemas.customer_preferences_response import (
    PreferredMenuListResponse,
    PreferredMenuCreateRequest,
    PreferredMenuDeleteRequest,
    NutritionTypeListResponse,
    NutritionTypeCreateRequest,
    NutritionTypeDeleteRequest,
    AllergyListResponse,
    AllergyCreateRequest,
    AllergyDeleteRequest,
    ToppingTypeListResponse,
    ToppingTypeCreateRequest,
    ToppingTypeDeleteRequest
)

from schemas.customer_profile import CustomerProfileResponse

from schemas.me import UserProfileMeResponse

router = APIRouter(prefix="/profile", tags=["Customer-Profile"])


@router.get(
    "",
    response_model=CustomerProfileResponse,
    responses=create_error_responses({
        401: ["인증 정보가 없음", "토큰 만료"]
    })
)
async def get_customer_profile_all(
    current_user: CurrentCustomerDep,
    profile_repo: CustomerProfileRepositoryDep
):
    """소비자의 모든 프로필 정보를 조회"""
    customer_email = current_user["sub"]
    
    profile_data = await profile_repo.get_all_profile_data(customer_email)
    
    return CustomerProfileResponse(**profile_data)


@router.get(
    "/me",
    response_model=UserProfileMeResponse,
    responses=create_error_responses({
        401: ["인증 정보가 없음", "토큰 만료"]
    })
)
async def get_customer_profile_all(
    current_user: CurrentCustomerDep
):
    """소비자 이메일 조회"""
    customer_email = current_user["sub"]
    
    return UserProfileMeResponse(email=customer_email)


@router.get(
    "/detail",
    response_model=CustomerDetailResponse,
    responses=create_error_responses({
        401: ["인증 정보가 없음", "토큰 만료"],
        404: ["소비자 상세 정보가 없음"]
    })
)
async def get_customer_detail(
    current_user: CurrentCustomerDep,
    customer_detail_repo: CustomerDetailRepositoryDep
):
    """소비자 상세 정보를 조회"""
    customer_email = current_user["sub"]
    
    detail = await customer_detail_repo.get_by_customer(customer_email)
    if not detail:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="소비자 상세 정보가 등록되지 않았습니다"
        )
    
    return detail


@router.patch(
    "/detail",
    response_model=CustomerDetailResponse,
    responses=create_error_responses({
        400: ["잘못된 입력 형식"],
        401: ["인증 정보가 없음", "토큰 만료"],
        404: ["소비자 상세 정보가 없음"]
    })
)
async def update_customer_detail(
    current_user: CurrentCustomerDep,
    customer_detail_repo: CustomerDetailRepositoryDep,
    detail_data: CustomerDetailUpdate
):
    """소비자 상세 정보를 수정합니다."""
    customer_email = current_user["sub"]
    
    # 수정할 데이터가 없는 경우
    update_dict = detail_data.model_dump(exclude_unset=True)
    if not update_dict:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="수정할 정보가 없습니다"
        )
    
    detail = await customer_detail_repo.update_for_customer(
        customer_email=customer_email,
        **update_dict
    )
    
    if not detail:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="소비자 상세 정보가 등록되지 않았습니다"
        )
    
    return detail


# 선호 메뉴 엔드포인트
@router.get(
    "/preferred-menus",
    response_model=PreferredMenuListResponse,
    responses=create_error_responses({
        401: ["인증 정보가 없음", "토큰 만료"]
    })
)
async def get_preferred_menus(
    current_user: CurrentCustomerDep,
    preferred_menu_repo: CustomerPreferredMenuRepositoryDep
):
    """소비자의 선호 메뉴 목록을 조회"""
    customer_email = current_user["sub"]
    menus = await preferred_menu_repo.get_by_customer(customer_email)
    return PreferredMenuListResponse(preferred_menus=menus)


@router.post(
    "/preferred-menus",
    response_model=PreferredMenuListResponse,
    status_code=status.HTTP_201_CREATED,
    responses=create_error_responses({
        400: ["잘못된 입력 형식", "중복된 메뉴"],
        401: ["인증 정보가 없음", "토큰 만료"]
    })
)
async def create_preferred_menus(
    current_user: CurrentCustomerDep,
    preferred_menu_repo: CustomerPreferredMenuRepositoryDep,
    menu_data: PreferredMenuCreateRequest
):
    """소비자의 선호 메뉴를 추가 - 여러 개를 한번에 추가할 수 있음"""
    customer_email = current_user["sub"]
    
    # 기존 메뉴 확인하여 중복 체크
    existing_menus = await preferred_menu_repo.get_by_customer(customer_email)
    existing_types = {menu.menu_type for menu in existing_menus}
    
    new_types = set(menu_data.menu_types)
    duplicates = new_types & existing_types
    
    if duplicates:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"이미 등록된 메뉴가 있습니다: {', '.join(d.value for d in duplicates)}"
        )
    
    # 새로운 메뉴 추가
    created_menus = await preferred_menu_repo.create_bulk_for_customer(
        customer_email=customer_email,
        menu_types=menu_data.menu_types
    )
    
    # 기존 메뉴 + 새로 생성된 메뉴
    all_menus = existing_menus + created_menus
    return PreferredMenuListResponse(preferred_menus=all_menus)


@router.delete(
    "/preferred-menus",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=create_error_responses({
        400: ["잘못된 입력 형식"],
        401: ["인증 정보가 없음", "토큰 만료"],
        404: ["선호 메뉴를 찾을 수 없음"]
    })
)
async def delete_preferred_menu(
    current_user: CurrentCustomerDep,
    preferred_menu_repo: CustomerPreferredMenuRepositoryDep,
    menu_data: PreferredMenuDeleteRequest
):
    """소비자의 특정 선호 메뉴를 삭제"""
    customer_email = current_user["sub"]
    
    deleted = await preferred_menu_repo.delete_for_customer(
        customer_email=customer_email,
        menu_type=menu_data.menu_type
    )
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="해당 선호 메뉴를 찾을 수 없습니다"
        )


# 영양 타입 엔드포인트
@router.get(
    "/nutrition-types",
    response_model=NutritionTypeListResponse,
    responses=create_error_responses({
        401: ["인증 정보가 없음", "토큰 만료"]
    })
)
async def get_nutrition_types(
    current_user: CurrentCustomerDep,
    nutrition_type_repo: CustomerNutritionTypeRepositoryDep
):
    """소비자의 영양 타입 목록을 조회"""
    customer_email = current_user["sub"]
    types = await nutrition_type_repo.get_by_customer(customer_email)
    return NutritionTypeListResponse(nutrition_types=types)


@router.post(
    "/nutrition-types",
    response_model=NutritionTypeListResponse,
    status_code=status.HTTP_201_CREATED,
    responses=create_error_responses({
        400: ["잘못된 입력 형식", "중복된 영양 타입"],
        401: ["인증 정보가 없음", "토큰 만료"]
    })
)
async def create_nutrition_types(
    current_user: CurrentCustomerDep,
    nutrition_type_repo: CustomerNutritionTypeRepositoryDep,
    type_data: NutritionTypeCreateRequest
):
    """소비자의 영양 타입을 추가. 여러 개를 한번에 추가할 수 있음."""
    customer_email = current_user["sub"]
    
    # 기존 타입 확인하여 중복 체크
    existing_types = await nutrition_type_repo.get_by_customer(customer_email)
    existing_nutrition_types = {t.nutrition_type for t in existing_types}
    
    new_types = set(type_data.nutrition_types)
    duplicates = new_types & existing_nutrition_types
    
    if duplicates:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"이미 등록된 영양 타입이 있습니다: {', '.join(d.value for d in duplicates)}"
        )
    
    # 새로운 타입 추가
    created_types = await nutrition_type_repo.create_bulk_for_customer(
        customer_email=customer_email,
        nutrition_types=type_data.nutrition_types
    )
    
    # 기존 타입 + 새로 생성된 타입
    all_types = existing_types + created_types
    return NutritionTypeListResponse(nutrition_types=all_types)


@router.delete(
    "/nutrition-types",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=create_error_responses({
        400: ["잘못된 입력 형식"],
        401: ["인증 정보가 없음", "토큰 만료"],
        404: ["영양 타입을 찾을 수 없음"]
    })
)
async def delete_nutrition_type(
    current_user: CurrentCustomerDep,
    nutrition_type_repo: CustomerNutritionTypeRepositoryDep,
    type_data: NutritionTypeDeleteRequest
):
    """소비자의 특정 영양 타입을 삭제"""
    customer_email = current_user["sub"]
    
    deleted = await nutrition_type_repo.delete_for_customer(
        customer_email=customer_email,
        nutrition_type=type_data.nutrition_type
    )
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="해당 영양 타입을 찾을 수 없습니다"
        )


# 알레르기 엔드포인트
@router.get(
    "/allergies",
    response_model=AllergyListResponse,
    responses=create_error_responses({
        401: ["인증 정보가 없음", "토큰 만료"]
    })
)
async def get_allergies(
    current_user: CurrentCustomerDep,
    allergy_repo: CustomerAllergyRepositoryDep
):
    """소비자의 알레르기 목록을 조회"""
    customer_email = current_user["sub"]
    allergies = await allergy_repo.get_by_customer(customer_email)
    return AllergyListResponse(allergies=allergies)


@router.post(
    "/allergies",
    response_model=AllergyListResponse,
    status_code=status.HTTP_201_CREATED,
    responses=create_error_responses({
        400: ["잘못된 입력 형식", "중복된 알레르기"],
        401: ["인증 정보가 없음", "토큰 만료"]
    })
)
async def create_allergies(
    current_user: CurrentCustomerDep,
    allergy_repo: CustomerAllergyRepositoryDep,
    allergy_data: AllergyCreateRequest
):
    """소비자의 알레르기를 추가. 여러 개를 한번에 추가할 수 있음."""
    customer_email = current_user["sub"]
    
    # 기존 알레르기 확인하여 중복 체크
    existing_allergies = await allergy_repo.get_by_customer(customer_email)
    existing_types = {allergy.allergy_type for allergy in existing_allergies}
    
    new_types = set(allergy_data.allergy_types)
    duplicates = new_types & existing_types
    
    if duplicates:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"이미 등록된 알레르기가 있습니다: {', '.join(d.value for d in duplicates)}"
        )
    
    # 새로운 알레르기 추가
    created_allergies = await allergy_repo.create_bulk_for_customer(
        customer_email=customer_email,
        allergy_types=allergy_data.allergy_types
    )
    
    # 기존 알레르기 + 새로 생성된 알레르기
    all_allergies = existing_allergies + created_allergies
    return AllergyListResponse(allergies=all_allergies)


@router.delete(
    "/allergies",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=create_error_responses({
        400: ["잘못된 입력 형식"],
        401: ["인증 정보가 없음", "토큰 만료"],
        404: ["알레르기를 찾을 수 없음"]
    })
)
async def delete_allergy(
    current_user: CurrentCustomerDep,
    allergy_repo: CustomerAllergyRepositoryDep,
    allergy_data: AllergyDeleteRequest
):
    """소비자의 특정 알레르기를 삭제"""
    customer_email = current_user["sub"]
    
    deleted = await allergy_repo.delete_for_customer(
        customer_email=customer_email,
        allergy_type=allergy_data.allergy_type
    )
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="해당 알레르기를 찾을 수 없습니다"
        )


# 토핑 타입 엔드포인트
@router.get(
    "/topping-types",
    response_model=ToppingTypeListResponse,
    responses=create_error_responses({
        401: ["인증 정보가 없음", "토큰 만료"]
    })
)
async def get_topping_types(
    current_user: CurrentCustomerDep,
    topping_type_repo: CustomerToppingTypeRepositoryDep
):
    """소비자의 토핑 타입 목록을 조회"""
    customer_email = current_user["sub"]
    types = await topping_type_repo.get_by_customer(customer_email)
    return ToppingTypeListResponse(topping_types=types)


@router.post(
    "/topping-types",
    response_model=ToppingTypeListResponse,
    status_code=status.HTTP_201_CREATED,
    responses=create_error_responses({
        400: ["잘못된 입력 형식", "중복된 토핑 타입"],
        401: ["인증 정보가 없음", "토큰 만료"]
    })
)
async def create_topping_types(
    current_user: CurrentCustomerDep,
    topping_type_repo: CustomerToppingTypeRepositoryDep,
    type_data: ToppingTypeCreateRequest
):
    """소비자의 토핑 타입을 추가. 여러 개를 한번에 추가할 수 있음."""
    customer_email = current_user["sub"]
    
    # 기존 타입 확인하여 중복 체크
    existing_types = await topping_type_repo.get_by_customer(customer_email)
    existing_topping_types = {t.topping_type for t in existing_types}
    
    new_types = set(type_data.topping_types)
    duplicates = new_types & existing_topping_types
    
    if duplicates:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"이미 등록된 토핑 타입이 있습니다: {', '.join(d.value for d in duplicates)}"
        )
    
    # 새로운 타입 추가
    created_types = await topping_type_repo.create_bulk_for_customer(
        customer_email=customer_email,
        topping_types=type_data.topping_types
    )
    
    # 기존 타입 + 새로 생성된 타입
    all_types = existing_types + created_types
    return ToppingTypeListResponse(topping_types=all_types)


@router.delete(
    "/topping-types",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=create_error_responses({
        400: ["잘못된 입력 형식"],
        401: ["인증 정보가 없음", "토큰 만료"],
        404: ["토핑 타입을 찾을 수 없음"]
    })
)
async def delete_topping_type(
    current_user: CurrentCustomerDep,
    topping_type_repo: CustomerToppingTypeRepositoryDep,
    type_data: ToppingTypeDeleteRequest
):
    """소비자의 특정 토핑 타입을 삭제"""
    customer_email = current_user["sub"]
    
    deleted = await topping_type_repo.delete_for_customer(
        customer_email=customer_email,
        topping_type=type_data.topping_type
    )
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="해당 토핑 타입을 찾을 수 없습니다"
        )