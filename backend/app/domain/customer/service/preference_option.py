from typing import List

from app.domain.seller.dto.nutrition import NUTRITION_TYPE_NAMES, NutritionType
from app.domain.customer.dto.preference_option import PreferenceOption
from app.domain.customer.dto.preference import (
    ALLERGY_TYPE_NAMES,
    AllergyType,
    PREFERRED_MENU_NAMES,
    PreferredMenu,
    TOPPING_TYPE_NAMES,
    ToppingType,
)


class PreferenceOptionService:
    """프론트 셀렉터에 그릴 옵션 목록을 만든다. 상태 없음."""

    def list_preferred_menus(self) -> List[PreferenceOption]:
        return [
            PreferenceOption(type=m.value, name=PREFERRED_MENU_NAMES[m])
            for m in PreferredMenu
        ]


    def list_nutrition_types(self) -> List[PreferenceOption]:
        return [
            PreferenceOption(type=n.value, name=NUTRITION_TYPE_NAMES[n])
            for n in NutritionType
        ]


    def list_allergy_types(self) -> List[PreferenceOption]:
        return [
            PreferenceOption(type=a.value, name=ALLERGY_TYPE_NAMES[a])
            for a in AllergyType
        ]


    def list_topping_types(self) -> List[PreferenceOption]:
        return [
            PreferenceOption(type=t.value, name=TOPPING_TYPE_NAMES[t])
            for t in ToppingType
        ]
