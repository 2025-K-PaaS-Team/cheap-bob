from fastapi import APIRouter, Depends
from dependency_injector.wiring import Provide, inject

from app.domain.customer.service.preference_option import PreferenceOptionService
from app.domain.customer.schema.preference_option import (
    AllergyTypeOptions,
    NutritionTypeOptions,
    PreferredMenuOptions,
    ToppingTypeOptions,
)


router = APIRouter(prefix="/options", tags=["Options-Info"])


@router.get("/preferred-menus", response_model=PreferredMenuOptions)
@inject
async def get_preferred_menu_options_list(
    service: PreferenceOptionService = Depends(Provide["preference_option_service"]),
):
    """선호 메뉴 옵션 목록."""
    return PreferredMenuOptions(options=service.list_preferred_menus())


@router.get("/nutrition-types", response_model=NutritionTypeOptions)
@inject
async def get_nutrition_type_options_list(
    service: PreferenceOptionService = Depends(Provide["preference_option_service"]),
):
    return NutritionTypeOptions(options=service.list_nutrition_types())


@router.get("/allergies", response_model=AllergyTypeOptions)
@inject
async def get_allergy_type_options_list(
    service: PreferenceOptionService = Depends(Provide["preference_option_service"]),
):
    return AllergyTypeOptions(options=service.list_allergy_types())


@router.get("/topping-types", response_model=ToppingTypeOptions)
@inject
async def get_topping_type_options_list(
    service: PreferenceOptionService = Depends(Provide["preference_option_service"]),
):
    return ToppingTypeOptions(options=service.list_topping_types())
