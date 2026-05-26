from typing import List
from pydantic import BaseModel, Field


class PreferenceOptionResponse(BaseModel):
    """프론트가 셀렉터에 그릴 옵션 한 줄."""
    type: str = Field(..., description="백엔드 식별 값")
    name: str = Field(..., description="사용자 노출 이름 (한국어)")

    model_config = {"from_attributes": True}


class PreferredMenuOptions(BaseModel):
    options: List[PreferenceOptionResponse]


class NutritionTypeOptions(BaseModel):
    options: List[PreferenceOptionResponse]


class AllergyTypeOptions(BaseModel):
    options: List[PreferenceOptionResponse]


class ToppingTypeOptions(BaseModel):
    options: List[PreferenceOptionResponse]
