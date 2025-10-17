import type {
  AllergieDeleteType,
  AllergiesBaseType,
  CustomerDetailBaseType,
  CustomerDetailType,
  CustomerRegisterResponseType,
  CustomerRegisterType,
  MenuBaseType,
  MenuDeleteType,
  PreferAllergiesType,
  PreferMenuType,
  PreferNutritionType,
  PreferToppingType,
  ToppingBaseType,
  ToppingDeleteType,
} from "@interface";
import { customerProfileApi, customerRegisterApi } from "@services/client";

// POST: create customer register
export const CreateCustomerRegister = async (
  body: CustomerRegisterType
): Promise<CustomerRegisterResponseType> => {
  const { data } = await customerRegisterApi.post("", body);

  return data;
};

// GET: get customer detail
export const GetCustomerDetail = async (): Promise<CustomerDetailType> => {
  const { data } = await customerProfileApi.get("/detail");

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
  body: string
): Promise<PreferNutritionType> => {
  const { data } = await customerProfileApi.post("/nutrition-types", {
    nutrition_types: [body],
  });

  return data;
};

// DELETE: delete nutrition types
export const DeleteNutrition = async (body: string) => {
  const { data } = await customerProfileApi.delete("/nutrition-types", {
    data: {
      nutrition_type: body,
    },
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
