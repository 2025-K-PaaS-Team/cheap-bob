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

// POST: add favorites store
export const AddFavoriteStore = async (storeId: string) => {
  const { data } = await customerSearchApi.post(`/${storeId}/favorites`);

  return data;
};

// DELETE : remove favorites store
export const RemoveFavoriteStore = async (storeId: string) => {
  const { data } = await customerSearchApi.delete(`/${storeId}/favorites`);

  return data;
};

// GET: get favorites store
export const GetFavoriteStore = async () => {
  const { data } = await customerSearchApi.get("/favorites");

  return data;
};
