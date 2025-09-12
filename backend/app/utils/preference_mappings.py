from typing import Dict, List
from schemas.food_preferences import PreferredMenu, NutritionType, AllergyType
from schemas.preference_options import PreferenceOption


# 선호 메뉴 이름 매핑
PREFERRED_MENU_NAMES: Dict[PreferredMenu, str] = {
    PreferredMenu.salad: "샐러드",
    PreferredMenu.poke: "포케",
    PreferredMenu.korean: "한식",
    PreferredMenu.sandwich: "샌드위치"
}


# 영양 타입 이름 매핑
NUTRITION_TYPE_NAMES: Dict[NutritionType, str] = {
    NutritionType.diet: "다이어트",
    NutritionType.LCHF: "저탄고지",
    NutritionType.protein: "단백질",
    NutritionType.LSLS: "저당저염",
    NutritionType.balance: "균형잡힌",
    NutritionType.vegetarian: "채식"
}


# 알레르기 이름 매핑
ALLERGY_TYPE_NAMES: Dict[AllergyType, str] = {
    AllergyType.seafood: "해산물",
    AllergyType.peanut: "땅콩",
    AllergyType.nuts: "견과류",
    AllergyType.soy: "대두",
    AllergyType.wheat: "밀",
    AllergyType.egg: "계란",
    AllergyType.dairy: "유제품",
    AllergyType.shellfish: "갑각류",
    AllergyType.fish: "어패류",
    AllergyType.pork: "돼지고기",
    AllergyType.beef: "쇠고기",
    AllergyType.chicken: "닭고기"
}


def get_preferred_menu_options() -> List[PreferenceOption]:
    """선호 메뉴 옵션 목록 반환"""
    return [
        PreferenceOption(type=menu.value, name=PREFERRED_MENU_NAMES[menu])
        for menu in PreferredMenu
    ]


def get_nutrition_type_options() -> List[PreferenceOption]:
    """영양 타입 옵션 목록 반환"""
    return [
        PreferenceOption(type=nutrition.value, name=NUTRITION_TYPE_NAMES[nutrition])
        for nutrition in NutritionType
    ]


def get_allergy_type_options() -> List[PreferenceOption]:
    """알레르기 타입 옵션 목록 반환"""
    return [
        PreferenceOption(type=allergy.value, name=ALLERGY_TYPE_NAMES[allergy])
        for allergy in AllergyType
    ]