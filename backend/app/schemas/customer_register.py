from typing import List, Optional
from pydantic import BaseModel, Field
from schemas.customer_detail import CustomerDetailResponse
from schemas.customer_preferences_response import (
    PreferredMenuResponse,
    NutritionTypeResponse,
    AllergyResponse,
    ToppingTypeResponse
)
from schemas.food_preferences import (
    PreferredMenu,
    NutritionType,
    AllergyType,
    ToppingType
)


class CustomerRegisterRequest(BaseModel):
    nickname: str = Field(..., min_length=1, max_length=7, description="닉네임 (1-7자)")
    phone_number: str = Field(..., pattern="^[0-9]{11}$", description="전화번호 (11자리 숫자)")
    preferred_menus: Optional[List[PreferredMenu]] = Field(None, description="선호 메뉴 목록")
    nutrition_types: Optional[List[NutritionType]] = Field(None, description="영양 타입 목록")
    allergies: Optional[List[AllergyType]] = Field(None, description="알레르기 목록")
    topping_types: Optional[List[ToppingType]] = Field(None, description="토핑 타입 목록")


class CustomerRegisterResponse(BaseModel):
    detail: CustomerDetailResponse = Field(..., description="고객 상세 정보")
    preferred_menus: List[PreferredMenuResponse] = Field(default_factory=list, description="선호 메뉴 목록")
    nutrition_types: List[NutritionTypeResponse] = Field(default_factory=list, description="영양 타입 목록")
    allergies: List[AllergyResponse] = Field(default_factory=list, description="알레르기 목록")
    topping_types: List[ToppingTypeResponse] = Field(default_factory=list, description="토핑 타입 목록")