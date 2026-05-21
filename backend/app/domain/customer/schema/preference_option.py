from typing import List
from pydantic import BaseModel, Field


class PreferenceOption(BaseModel):
    """프론트가 셀렉터에 그릴 옵션 한 줄."""
    type: str = Field(..., description="백엔드 식별 값")
    name: str = Field(..., description="사용자 노출 이름 (한국어)")


class PreferredMenuOptions(BaseModel):
    options: List[PreferenceOption]


class NutritionTypeOptions(BaseModel):
    options: List[PreferenceOption]


class AllergyTypeOptions(BaseModel):
    options: List[PreferenceOption]


class ToppingTypeOptions(BaseModel):
    options: List[PreferenceOption]
