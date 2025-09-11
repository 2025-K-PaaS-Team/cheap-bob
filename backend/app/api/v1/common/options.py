from fastapi import APIRouter

from schemas.preference_options import (
    PreferredMenuOptions,
    NutritionTypeOptions,
    AllergyTypeOptions
)
from utils.preference_mappings import (
    get_preferred_menu_options,
    get_nutrition_type_options,
    get_allergy_type_options
)


router = APIRouter(prefix="/options", tags=["Options-Info"])

# 옵션 정보 엔드포인트
@router.get(
    "/preferred-menus",
    response_model=PreferredMenuOptions
)
async def get_preferred_menu_options_list():
    """선호 메뉴 옵션 목록을 조회"""
    options = get_preferred_menu_options()
    return PreferredMenuOptions(options=options)


@router.get(
    "/nutrition-types",
    response_model=NutritionTypeOptions
)
async def get_nutrition_type_options_list():
    """영양 타입 옵션 목록을 조회"""
    options = get_nutrition_type_options()
    return NutritionTypeOptions(options=options)


@router.get(
    "/allergies",
    response_model=AllergyTypeOptions
)
async def get_allergy_type_options_list():
    """알레르기 타입 옵션 목록을 조회"""
    options = get_allergy_type_options()
    return AllergyTypeOptions(options=options)