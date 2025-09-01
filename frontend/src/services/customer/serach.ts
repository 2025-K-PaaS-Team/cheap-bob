import { customerSearchApi } from "@services/client";

// GET: get stores products
export const getStores = async () => {
  const { data } = await customerSearchApi.get("");
  return data;
};

// GET: get specific store products
export const getSpecificStore = async (storeId: string) => {
  const { data } = await customerSearchApi.get(`/${storeId}/products`);
  return data;
};
