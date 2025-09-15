import type {
  AllergieDeleteType,
  AllergiesBaseType,
  CheckCustomerDetailType,
  CustomerDetailBaseType,
  CustomerDetailType,
  MenuBaseType,
  MenuDeleteType,
  NutritionBaseType,
  NutritionDeleteType,
  PreferAllergiesType,
  PreferMenuType,
  PreferNutritionType,
  PreferToppingType,
  ToppingBaseType,
  ToppingDeleteType,
} from "@interface";
import { customerProfileApi } from "@services/client";

// GET: check customer detail(2-step user info)
export const CheckCustomerDetail =
  async (): Promise<CheckCustomerDetailType> => {
    const { data } = await customerProfileApi.get("/check");

    return data;
  };

// POST: create customer detail
export const CreateCustomerDetail = async (
  body: CustomerDetailBaseType
): Promise<CustomerDetailType> => {
  const { data } = await customerProfileApi.post("/detail", body);

  return data;
};

// PATCH: update customer detail
export const UpdateCustomerDetail = async (
  body: CustomerDetailBaseType
): Promise<CustomerDetailType> => {
  const { data } = await customerProfileApi.patch("/detail", body);

  return data;
};

// GET: get preferred menus
export const GetPreferMenu = async (): Promise<PreferMenuType> => {
  const { data } = await customerProfileApi.get("/preferred-menus");

  return data;
};

// POST: create preferred menus
export const CreatePreferMenu = async (
  body: MenuBaseType
): Promise<PreferMenuType> => {
  const { data } = await customerProfileApi.post("/preferred-menus", body);

  return data;
};

// DELETE: delete preferred menu
export const DeletePreferMenu = async (body: MenuDeleteType) => {
  const { data } = await customerProfileApi.delete("/preferred-menus", {
    data: body,
  });

  return data;
};

// GET: get nutrition types
export const GetNutrition = async (): Promise<PreferNutritionType> => {
  const { data } = await customerProfileApi.get("/nutrition-types");

  return data;
};

// POST: create nutrition types
export const CrateNutrition = async (
  body: NutritionBaseType
): Promise<PreferNutritionType> => {
  const { data } = await customerProfileApi.post("/nutrition-types", body);

  return data;
};

// DELETE: delete preferred menu
export const DeleteNutrition = async (body: NutritionDeleteType) => {
  const { data } = await customerProfileApi.delete("/nutrition-types", {
    data: body,
  });

  return data;
};

// GET: get allergies
export const GetAllergies = async (): Promise<PreferAllergiesType> => {
  const { data } = await customerProfileApi.get("/allergies");

  return data;
};

// POST: create allergies
export const CreateAllergies = async (
  body: AllergiesBaseType
): Promise<PreferAllergiesType> => {
  const { data } = await customerProfileApi.post("/allergies", body);

  return data;
};

// DELETE: delete allergy
export const DeleteAllergies = async (body: AllergieDeleteType) => {
  const { data } = await customerProfileApi.delete("/allergies", {
    data: body,
  });

  return data;
};

// GET: get Topping
export const GetTopping = async (): Promise<PreferToppingType> => {
  const { data } = await customerProfileApi.get("/topping-types");

  return data;
};

// POST: create Topping
export const CreateTopping = async (
  body: ToppingBaseType
): Promise<PreferToppingType> => {
  const { data } = await customerProfileApi.post("/topping-types", body);

  return data;
};

// DELETE: delete Topping
export const DeleteTopping = async (body: ToppingDeleteType) => {
  const { data } = await customerProfileApi.delete("/topping-types", {
    data: body,
  });

  return data;
};
