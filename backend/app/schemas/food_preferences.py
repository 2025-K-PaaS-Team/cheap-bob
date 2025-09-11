import enum

class PreferredMenu(enum.Enum):
    """선호 메뉴"""
    salad = "salad" # 샐러드
    poke = "poke" # 포케
    korean = "korean" # 한식
    sandwich = "sandwich" # 샌드위치


class NutritionType(enum.Enum):
    """식품 영양"""
    diet = "diet" # 다이어트
    LCHF = "LCHF" # 저탄고지(low_carb_high_fat)
    protein = "protein" # 단백질
    LSLS = "LSLS" # 저당저염(low_sugar_low_salt)
    balance = "balance" # 균형잡힌
    vegetarian = "vegetarian" # 채식


class AllergyType(enum.Enum):
    """제약 조건"""
    seafood = "seafood" # 해산물
    peanut = "peanut" # 땅콩
    nuts = "nuts" # 견과류
    soy = "soy" # 대두
    wheat = "wheat" # 밀
    egg = "egg" # 계란
    dairy = "dairy" # 유제품
    shellfish = "shellfish" # 갑각류
    fish = "fish" # 어패류
    pork = "pork" #돼지고기
    beef = "beef" # 쇠고기
    chicken = "chicken" # 닭고기