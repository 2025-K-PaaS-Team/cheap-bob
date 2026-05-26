import enum


class NutritionType(enum.Enum):
    """상품 영양 분류. ProductNutrition / CustomerNutritionType 양쪽이 공유."""
    diet = "diet"             # 다이어트
    lchf = "lchf"             # 저탄고지
    protein = "protein"       # 단백질
    lsls = "lsls"             # 저당저염
    balance = "balance"       # 균형잡힌
    vegetarian = "vegetarian" # 채식


# 프론트 셀렉터/뱃지에 표시할 한국어 라벨.
NUTRITION_TYPE_NAMES: dict[NutritionType, str] = {
    NutritionType.diet: "다이어트",
    NutritionType.lchf: "저탄고지",
    NutritionType.protein: "단백질",
    NutritionType.lsls: "저당저염",
    NutritionType.balance: "균형잡힌",
    NutritionType.vegetarian: "채식",
}
