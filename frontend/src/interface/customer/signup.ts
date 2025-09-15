import type { TimeStamp } from "@interface/common/types";

export type CustomerDetailBaseType = {
  nickname: string;
  phone_number: string;
};

export type CustomerDetailType = CustomerDetailBaseType & {
  customer_email: string;
  created_at: TimeStamp;
  updated_at: TimeStamp;
};

export type CheckCustomerDetailType = {
  has_detail: boolean;
  detail: CustomerDetailType;
};

export type MenuBaseType = {
  menu_types: string[];
};

export type MenuDeleteType = {
  menu_type: string;
};

export type PreferMenuBaseType = {
  menu_type: string;
  id: number;
  created_at: TimeStamp;
};

export type PreferMenuType = {
  preferred_menus: PreferMenuBaseType[];
};

export type NutritionBaseType = {
  nutrition_types: string[];
};

export type NutritionDeleteType = {
  nutrition_type: string;
};

export type PreferNutritionBaseType = {
  id: number;
  nutrition_type: string;
  created_at: TimeStamp;
};

export type PreferNutritionType = {
  nutrition_types: PreferNutritionBaseType[];
};

export type AllergiesBaseType = {
  allergy_types: string[];
};

export type AllergieDeleteType = {
  allergy_type: string;
};

export type PreferAllergiesBaseType = {
  id: number;
  allergy_type: string;
  created_at: TimeStamp;
};

export type PreferAllergiesType = {
  allergies: PreferAllergiesBaseType[];
};

export type ToppingBaseType = {
  topping_types: string[];
};

export type PreferToppingBaseType = {
  id: number;
  topping_type: string;
  created_at: TimeStamp;
};

export type PreferToppingType = {
  topping_types: PreferToppingBaseType[];
};

export type ToppingDeleteType = {
  topping_type: string;
};
