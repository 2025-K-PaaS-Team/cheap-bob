import { sellerStoreApi } from "@services/client";

import type {
  StorePaymentInfoRequestType,
  StorePaymentInfoResponseType,
  StorePaymentStatusType,
  StoreRequestType,
  StoreResponseType,
  StoreWithProductResponseType,
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

// GET: get store products
export const getStoreProduct = async (
  storeId: string
): Promise<StoreWithProductResponseType> => {
  const { data } = await sellerStoreApi.get<StoreWithProductResponseType>(
    `/${storeId}/products`
  );

  return data;
};

// GET: get payment info status
export const getStorePaymentStatus = async (
  storeId: string
): Promise<StorePaymentStatusType> => {
  const { data } = await sellerStoreApi.get<StorePaymentStatusType>(
    `/${storeId}/payment-info/status`
  );

  return data;
};

// POST: register store payment info
export const registerStorePayment = async (
  storeId: string,
  body: StorePaymentInfoRequestType
): Promise<StorePaymentInfoResponseType> => {
  const { data } = await sellerStoreApi.post<StorePaymentInfoResponseType>(
    `/${storeId}/payment-info`,
    body
  );

  return data;
};
