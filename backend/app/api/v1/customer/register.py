from fastapi import APIRouter, HTTPException, status

from utils.docs_error import create_error_responses
from api.deps.auth import CurrentCustomerDep
from api.deps.repository import (
    CustomerDetailRepositoryDep,
    CustomerPreferredMenuRepositoryDep,
    CustomerNutritionTypeRepositoryDep,
    CustomerAllergyRepositoryDep,
    CustomerToppingTypeRepositoryDep
)
from schemas.customer_register import CustomerRegisterRequest, CustomerRegisterResponse


router = APIRouter(prefix="/register", tags=["Customer-Register"])


@router.post(
    "",
    response_model=CustomerRegisterResponse,
    status_code=status.HTTP_201_CREATED,
    responses=create_error_responses({
        400: ["이미 프로필이 존재함", "잘못된 입력 형식"],
        401: ["인증 정보가 없음", "토큰 만료"],
    })
)
async def customer_register(
    current_user: CurrentCustomerDep,
    register_data: CustomerRegisterRequest,
    detail_repo: CustomerDetailRepositoryDep,
    preferred_menu_repo: CustomerPreferredMenuRepositoryDep,
    nutrition_type_repo: CustomerNutritionTypeRepositoryDep,
    allergy_repo: CustomerAllergyRepositoryDep,
    topping_type_repo: CustomerToppingTypeRepositoryDep
):
    """소비자 통합 회원가입 - 상세정보, 선호메뉴, 영양타입, 알레르기, 토핑타입을 한번에 등록"""
    customer_email = current_user["sub"]
    
    # 이미 상세 정보가 존재하는지 확인
    existing = await detail_repo.exists_for_customer(customer_email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 프로필이 등록되어 있습니다"
        )
    
    # 고객 상세 정보 생성
    detail = await detail_repo.create_for_customer(
        customer_email=customer_email,
        nickname=register_data.nickname,
        phone_number=register_data.phone_number
    )
    
    # 선호 메뉴 생성
    preferred_menus = []
    if register_data.preferred_menus:
        preferred_menus = await preferred_menu_repo.create_bulk_for_customer(
            customer_email=customer_email,
            menu_types=register_data.preferred_menus
        )
    
    # 영양 타입 생성
    nutrition_types = []
    if register_data.nutrition_types:
        nutrition_types = await nutrition_type_repo.create_bulk_for_customer(
            customer_email=customer_email,
            nutrition_types=register_data.nutrition_types
        )
    
    # 알레르기 생성
    allergies = []
    if register_data.allergies:
        allergies = await allergy_repo.create_bulk_for_customer(
            customer_email=customer_email,
            allergy_types=register_data.allergies
        )
    
    # 토핑 타입 생성
    topping_types = []
    if register_data.topping_types:
        topping_types = await topping_type_repo.create_bulk_for_customer(
            customer_email=customer_email,
            topping_types=register_data.topping_types
        )
    
    return CustomerRegisterResponse(
        detail=detail,
        preferred_menus=preferred_menus,
        nutrition_types=nutrition_types,
        allergies=allergies,
        topping_types=topping_types
    )