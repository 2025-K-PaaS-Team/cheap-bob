from typing import List, Optional
from pydantic import BaseModel, Field

from app.domain.customer.schema.customer_preference import (
    AllergyResponse,
    NutritionTypeResponse,
    PreferredMenuResponse,
    ToppingTypeResponse,
)
from app.domain.customer.schema.customer_detail import CustomerDetailResponse
from app.domain.customer.dto.preference import (
    AllergyType,
    NutritionType,
    PreferredMenu,
    ToppingType,
)


class CustomerRegisterRequest(BaseModel):
    nickname: str = Field(..., min_length=1, max_length=7, description="닉네임 (1-7자)")
    phone_number: str = Field(..., pattern="^[0-9]{11}$", description="전화번호 (11자리 숫자)")
    preferred_menus: Optional[List[PreferredMenu]] = Field(None)
    nutrition_types: Optional[List[NutritionType]] = Field(None)
    allergies: Optional[List[AllergyType]] = Field(None)
    topping_types: Optional[List[ToppingType]] = Field(None)


class CustomerRegisterResponse(BaseModel):
    detail: CustomerDetailResponse
    preferred_menus: List[PreferredMenuResponse] = Field(default_factory=list)
    nutrition_types: List[NutritionTypeResponse] = Field(default_factory=list)
    allergies: List[AllergyResponse] = Field(default_factory=list)
    topping_types: List[ToppingTypeResponse] = Field(default_factory=list)
