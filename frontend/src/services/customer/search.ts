import type { StoreSearchType } from "@interface";
import { customerSearchApi } from "@services/client";

// GET: get stores products
export const getStores = async (page: number): Promise<StoreSearchType> => {
  const { data } = await customerSearchApi.get("", {
    params: { page },
  });
  return data;
};

// GET: get specific store products
export const getSpecificStore = async (storeId: string) => {
  const { data } = await customerSearchApi.get(`/${storeId}/products`);
  return data;
};
