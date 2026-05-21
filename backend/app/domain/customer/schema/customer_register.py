from typing import List, Optional
from pydantic import Field

from app.domain.seller.dto.nutrition import NutritionType
from app.domain.customer.schema.customer_detail import CustomerDetailBase
from app.domain.customer.dto.preference import (
    AllergyType,
    PreferredMenu,
    ToppingType,
)


class CustomerRegisterRequest(CustomerDetailBase):
    """2차 회원가입 요청. 닉네임 / 전화번호 규칙은 [[CustomerDetailBase]] 재사용."""
    preferred_menus: Optional[List[PreferredMenu]] = Field(None)
    nutrition_types: Optional[List[NutritionType]] = Field(None)
    allergies: Optional[List[AllergyType]] = Field(None)
    topping_types: Optional[List[ToppingType]] = Field(None)
