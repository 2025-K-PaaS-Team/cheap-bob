import type { NutritionBase } from "@interface";

export type SelectItem = { key: string; title: string; desc?: string };

export const NutritionList: {
  key: NutritionBase;
  title: string;
  desc?: string;
}[] = [
  { key: "diet", title: "다이어트", desc: "체지방 감소와 활력 증진" },
  { key: "LCHF", title: "저탄고지", desc: "식곤증 없는 안정적 에너지" },
  { key: "protein", title: "단백질 보충", desc: "근육 성장과 체력 강화" },
  { key: "LSLS", title: "저당저염", desc: "만성질환 예방과 저속노화" },
  { key: "balance", title: "균형잡힌", desc: "영양 충전으로 활기차게" },
  { key: "vegetarian", title: "채식 위주", desc: "심장 건강 개선과 체중감량" },
];

export const MenuList: SelectItem[] = [
  { key: "salad", title: "샐러드" },
  { key: "poke", title: "포케" },
  { key: "korean", title: "도시락" },
  { key: "sandwich", title: "샌드위치" },
];

export const ToppingList: SelectItem[] = [
  { key: "egg_mayo", title: "에그마요" },
  { key: "chicken_breast", title: "닭가슴살" },
  { key: "onion_flake", title: "어니언 후레이크" },
  { key: "toasted_bread", title: "구운 식빵" },
  { key: "sweet_pumpkin", title: "단호박" },
  { key: "ricotta_cheese", title: "리코타치즈" },
  { key: "shrimp", title: "새우" },
  { key: "smoked_salmon", title: "훈제연어" },
  { key: "avocado", title: "아보카도" },
  { key: "pork_belly", title: "우삼겹" },
];

export const AllergyList: SelectItem[] = [
  { key: "seafood", title: "해산물" },
  { key: "peanut", title: "땅콩" },
  { key: "nuts", title: "견과류" },
  { key: "soy", title: "대두" },
  { key: "wheat", title: "밀" },
  { key: "egg", title: "계란" },
  { key: "dairy", title: "유제품" },
  { key: "shellfish", title: "갑각류" },
  { key: "fish", title: "어패류" },
  { key: "pork", title: "돼지고기" },
  { key: "beef", title: "쇠고기" },
  { key: "chicken", title: "닭고기" },
];
