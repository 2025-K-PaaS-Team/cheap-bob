from typing import List
from pydantic import BaseModel, Field


class PreferenceOption(BaseModel):
    """선호도 옵션 스키마"""
    type: str = Field(..., description="백엔드에서 사용하는 값")
    name: str = Field(..., description="사용자에게 표시할 이름")


class PreferredMenuOptions(BaseModel):
    """선호 메뉴 옵션 목록"""
    options: List[PreferenceOption] = Field(..., description="선호 메뉴 옵션 목록")


class NutritionTypeOptions(BaseModel):
    """영양 타입 옵션 목록"""
    options: List[PreferenceOption] = Field(..., description="영양 타입 옵션 목록")


class AllergyTypeOptions(BaseModel):
    """알레르기 타입 옵션 목록"""
    options: List[PreferenceOption] = Field(..., description="알레르기 타입 옵션 목록")


class ToppingTypeOptions(BaseModel):
    """토핑 타입 옵션 목록"""
    options: List[PreferenceOption] = Field(..., description="토핑 타입 옵션 목록")