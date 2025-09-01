import { sellerStoreApi } from "@services/client";

import type {
  StoreRequestType,
  StoreResponseType,
} from "@interface/seller/types";

// POST: create store
export const createStore = async (
  body: StoreRequestType
): Promise<StoreResponseType> => {
  const { data } = await sellerStoreApi.post<StoreResponseType>("", body);

  return data;
};

// GET: get my store
export const getStore = async (): Promise<StoreResponseType> => {
  const { data } = await sellerStoreApi.get<StoreResponseType>("");

  return data;
};

// PUT: update my store
export const updateStore = async (
  storeId: string,
  body: StoreRequestType
): Promise<StoreResponseType> => {
  const { data } = await sellerStoreApi.put<StoreResponseType>(
    `/${storeId}`,
    body
  );
  return data;
};

// DELETE: delete my store
export const deleteStore = async (storeId: string): Promise<void> => {
  await sellerStoreApi.delete<StoreResponseType>(`/${storeId}`);
};
