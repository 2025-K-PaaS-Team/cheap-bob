from pydantic import BaseModel, Field
from typing import List

from schemas.customer_detail import CustomerDetailResponse
from schemas.customer_preferences_response import PreferredMenuResponse, NutritionTypeResponse, AllergyResponse, ToppingTypeResponse

class CustomerProfileResponse(BaseModel):
    """고객 프로필 전체 정보 응답 스키마"""
    detail: CustomerDetailResponse = Field(..., description="고객 상세 정보")
    preferred_menus: List[PreferredMenuResponse] = Field(default_factory=list, description="선호 메뉴 목록")
    nutrition_types: List[NutritionTypeResponse] = Field(default_factory=list, description="영양 타입 목록")
    allergies: List[AllergyResponse] = Field(default_factory=list, description="알레르기 목록")
    topping_types: List[ToppingTypeResponse] = Field(default_factory=list, description="토핑 타입 목록")