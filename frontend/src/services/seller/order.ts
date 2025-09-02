import type {
  CancelOrderRequestType,
  GetStoreOrderType,
  UpdateOrderAcceptType,
} from "@interface";
import { sellerOrderApi } from "@services/client";

// GET: get store orders
export const getStoreOrder = async (
  storeId: string
): Promise<GetStoreOrderType> => {
  const { data } = await sellerOrderApi.get(`/${storeId}`);

  return data;
};

// GET: get pending orders
export const getStorePendingOrder = async (
  storeId: string
): Promise<GetStoreOrderType> => {
  const { data } = await sellerOrderApi.get(`/${storeId}/pending`);

  return data;
};

// PATCH: udpate order accept
export const updateOrderAccept = async (
  paymentId: string
): Promise<UpdateOrderAcceptType> => {
  const { data } = await sellerOrderApi.patch(`/${paymentId}/accept`);

  return data;
};

// POST: cancel order
export const cancelOrder = async (
  paymentId: string,
  body: CancelOrderRequestType
) => {
  const { data } = await sellerOrderApi.post(`/${paymentId}/cancel`, body);

  return data;
};
