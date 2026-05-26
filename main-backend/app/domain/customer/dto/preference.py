import enum


class PreferredMenu(enum.Enum):
    """선호 메뉴."""
    salad = "salad"           # 샐러드
    poke = "poke"             # 포케
    korean = "korean"         # 한식
    sandwich = "sandwich"     # 샌드위치


class AllergyType(enum.Enum):
    """알레르기 / 제약 조건."""
    seafood = "seafood"
    peanut = "peanut"
    nuts = "nuts"
    soy = "soy"
    wheat = "wheat"
    egg = "egg"
    dairy = "dairy"
    shellfish = "shellfish"
    fish = "fish"
    pork = "pork"
    beef = "beef"
    chicken = "chicken"


class ToppingType(enum.Enum):
    """토핑 종류."""
    egg_mayo = "egg_mayo"
    chicken_breast = "chicken_breast"
    onion_flake = "onion_flake"
    toasted_bread = "toasted_bread"
    sweet_pumpkin = "sweet_pumpkin"
    ricotta_cheese = "ricotta_cheese"
    shrimp = "shrimp"
    smoked_salmon = "smoked_salmon"
    avocado = "avocado"
    pork_belly = "pork_belly"


# 프론트가 셀렉터에 표시할 한국어 라벨. /common/options 응답이 이 매핑을 그대로 노출한다.
PREFERRED_MENU_NAMES: dict[PreferredMenu, str] = {
    PreferredMenu.salad: "샐러드",
    PreferredMenu.poke: "포케",
    PreferredMenu.korean: "한식",
    PreferredMenu.sandwich: "샌드위치",
}

ALLERGY_TYPE_NAMES: dict[AllergyType, str] = {
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
    AllergyType.chicken: "닭고기",
}

TOPPING_TYPE_NAMES: dict[ToppingType, str] = {
    ToppingType.egg_mayo: "에그마요",
    ToppingType.chicken_breast: "닭가슴살",
    ToppingType.onion_flake: "어니언 후레이크",
    ToppingType.toasted_bread: "구운 식빵",
    ToppingType.sweet_pumpkin: "단호박",
    ToppingType.ricotta_cheese: "리코타치즈",
    ToppingType.shrimp: "새우",
    ToppingType.smoked_salmon: "훈제연어",
    ToppingType.avocado: "아보카도",
    ToppingType.pork_belly: "우삼겹",
}
