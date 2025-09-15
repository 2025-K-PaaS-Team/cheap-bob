import type { optionType } from "@interface/customer/option";
import { optionInfoApi } from "@services/client";

// GET: Get preferred Menu option list
export const getMenuOptionList = async (): Promise<optionType> => {
  const { data } = await optionInfoApi.get("/preferred-menus");

  return data;
};

// GET: Get nutrition Menu option list
export const GetNutritionOptionList = async (): Promise<optionType> => {
  const { data } = await optionInfoApi.get("/nutrition-types");

  return data;
};

// GET: Get Allegy Menu option list
export const GetAllegyOptionList = async (): Promise<optionType> => {
  const { data } = await optionInfoApi.get("/allergies");

  return data;
};

// GET: Get Topping Menu option list
export const GetToppingOptionList = async (): Promise<optionType> => {
  const { data } = await optionInfoApi.get("/topping-types");

  return data;
};
