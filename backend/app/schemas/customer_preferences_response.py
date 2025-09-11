from datetime import datetime
from typing import List
from pydantic import BaseModel, Field
from schemas.food_preferences import PreferredMenu, NutritionType, AllergyType


class PreferredMenuResponse(BaseModel):
    """선호 메뉴 응답 스키마"""
    id: int = Field(..., description="ID")
    menu_type: PreferredMenu = Field(..., description="메뉴 타입")
    created_at: datetime = Field(..., description="생성 일자")
    
    model_config = {
        "from_attributes": True
    }


class NutritionTypeResponse(BaseModel):
    """영양 타입 응답 스키마"""
    id: int = Field(..., description="ID")
    nutrition_type: NutritionType = Field(..., description="영양 타입")
    created_at: datetime = Field(..., description="생성 일자")
    
    model_config = {
        "from_attributes": True
    }


class AllergyResponse(BaseModel):
    """알레르기 응답 스키마"""
    id: int = Field(..., description="ID")
    allergy_type: AllergyType = Field(..., description="알레르기 타입")
    created_at: datetime = Field(..., description="생성 일자")
    
    model_config = {
        "from_attributes": True
    }


class PreferredMenuListResponse(BaseModel):
    """선호 메뉴 목록 응답 스키마"""
    preferred_menus: List[PreferredMenuResponse] = Field(..., description="선호 메뉴 목록")


class NutritionTypeListResponse(BaseModel):
    """영양 타입 목록 응답 스키마"""
    nutrition_types: List[NutritionTypeResponse] = Field(..., description="영양 타입 목록")


class AllergyListResponse(BaseModel):
    """알레르기 목록 응답 스키마"""
    allergies: List[AllergyResponse] = Field(..., description="알레르기 목록")


class PreferredMenuCreateRequest(BaseModel):
    """선호 메뉴 생성 요청 스키마"""
    menu_types: List[PreferredMenu] = Field(..., description="추가할 메뉴 타입 목록")


class NutritionTypeCreateRequest(BaseModel):
    """영양 타입 생성 요청 스키마"""
    nutrition_types: List[NutritionType] = Field(..., description="추가할 영양 타입 목록")


class AllergyCreateRequest(BaseModel):
    """알레르기 생성 요청 스키마"""
    allergy_types: List[AllergyType] = Field(..., description="추가할 알레르기 타입 목록")


class PreferredMenuDeleteRequest(BaseModel):
    """선호 메뉴 삭제 요청 스키마"""
    menu_type: PreferredMenu = Field(..., description="삭제할 메뉴 타입")


class NutritionTypeDeleteRequest(BaseModel):
    """영양 타입 삭제 요청 스키마"""
    nutrition_type: NutritionType = Field(..., description="삭제할 영양 타입")


class AllergyDeleteRequest(BaseModel):
    """알레르기 삭제 요청 스키마"""
    allergy_type: AllergyType = Field(..., description="삭제할 알레르기 타입")