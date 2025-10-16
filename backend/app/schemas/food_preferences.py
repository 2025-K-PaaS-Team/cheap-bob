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


class ToppingType(enum.Enum):
    """토핑 종류"""
    egg_mayo = "egg_mayo" # 에그마요
    chicken_breast = "chicken_breast" # 닭가슴살
    onion_flake = "onion_flake" # 어니언 후레이크
    toasted_bread = "toasted_bread" # 구운 식빵
    sweet_pumpkin = "sweet_pumpkin" # 단호박
    ricotta_cheese = "ricotta_cheese" # 리코타치즈
    shrimp = "shrimp" # 새우
    smoked_salmon = "smoked_salmon" # 훈제연어
    avocado = "avocado" # 아보카도
    pork_belly = "pork_belly" # 우삼겹