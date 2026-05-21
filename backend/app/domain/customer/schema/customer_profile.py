from typing import List
from pydantic import BaseModel, Field

from app.domain.customer.schema.customer_preference import (
    AllergyResponse,
    NutritionTypeResponse,
    PreferredMenuResponse,
    ToppingTypeResponse,
)
from app.domain.customer.schema.customer_detail import CustomerDetailResponse


class CustomerProfileResponse(BaseModel):
    """detail + 4종 선호의 통합 응답.

    `from_attributes=True` 로 서비스가 반환하는 [[CustomerFullProfile]] dataclass 를
    그대로 `model_validate` 할 수 있다.
    """

    detail: CustomerDetailResponse = Field(..., description="고객 상세 정보")
    preferred_menus: List[PreferredMenuResponse] = Field(default_factory=list)
    nutrition_types: List[NutritionTypeResponse] = Field(default_factory=list)
    allergies: List[AllergyResponse] = Field(default_factory=list)
    topping_types: List[ToppingTypeResponse] = Field(default_factory=list)

    model_config = {"from_attributes": True}
