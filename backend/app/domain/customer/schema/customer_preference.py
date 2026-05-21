from typing import List
from pydantic import BaseModel, Field
from datetime import datetime

from app.domain.customer.dto.preference import (
    AllergyType,
    NutritionType,
    PreferredMenu,
    ToppingType,
)


# ───────── 단건 응답 ─────────


class PreferredMenuResponse(BaseModel):
    id: int
    menu_type: PreferredMenu
    created_at: datetime
    model_config = {"from_attributes": True}


class NutritionTypeResponse(BaseModel):
    id: int
    nutrition_type: NutritionType
    created_at: datetime
    model_config = {"from_attributes": True}


class AllergyResponse(BaseModel):
    id: int
    allergy_type: AllergyType
    created_at: datetime
    model_config = {"from_attributes": True}


class ToppingTypeResponse(BaseModel):
    id: int
    topping_type: ToppingType
    created_at: datetime
    model_config = {"from_attributes": True}


# ───────── 목록 응답 ─────────


class PreferredMenuListResponse(BaseModel):
    preferred_menus: List[PreferredMenuResponse]


class NutritionTypeListResponse(BaseModel):
    nutrition_types: List[NutritionTypeResponse]


class AllergyListResponse(BaseModel):
    allergies: List[AllergyResponse]


class ToppingTypeListResponse(BaseModel):
    topping_types: List[ToppingTypeResponse]


# ───────── 생성 요청 (목록) ─────────


class PreferredMenuCreateRequest(BaseModel):
    menu_types: List[PreferredMenu] = Field(..., description="추가할 메뉴 타입 목록")


class NutritionTypeCreateRequest(BaseModel):
    nutrition_types: List[NutritionType] = Field(..., description="추가할 영양 타입 목록")


class AllergyCreateRequest(BaseModel):
    allergy_types: List[AllergyType] = Field(..., description="추가할 알레르기 목록")


class ToppingTypeCreateRequest(BaseModel):
    topping_types: List[ToppingType] = Field(..., description="추가할 토핑 타입 목록")


# ───────── 삭제 요청 (단건) ─────────


class PreferredMenuDeleteRequest(BaseModel):
    menu_type: PreferredMenu


class NutritionTypeDeleteRequest(BaseModel):
    nutrition_type: NutritionType


class AllergyDeleteRequest(BaseModel):
    allergy_type: AllergyType


class ToppingTypeDeleteRequest(BaseModel):
    topping_type: ToppingType
