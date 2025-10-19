import type { StoreSearchType } from "@interface";
import { customerSearchApi, customerSearchHistoryApi } from "@services/client";

// GET: get stores products
export const getStores = async (page: number): Promise<StoreSearchType> => {
  const { data } = await customerSearchApi.get("", {
    params: { page },
  });
  return data;
};

// GET: get specific store products
export const getStoreProduct = async (storeId: string) => {
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

// GET: get search history
export const GetSearchHistory = async () => {
  const { data } = await customerSearchHistoryApi.get("");

  return data;
};

// DELETE: remove search name
export const DeleteSearchByName = async (name: string) => {
  const { data } = await customerSearchHistoryApi.delete(`/${name}`);

  return data;
};

// GET: get stores by name
export const GetStoreByName = async (name: string, page: number = 0) => {
  const { data } = await customerSearchApi("/by-name", {
    params: {
      search_name: name,
      page: page,
    },
  });

  return data;
};
