import type {
  CancelOrderResponseType,
  DashboardResponseType,
  GetQrCodeType,
  GetStoreOrderType,
  UpdateOrderAcceptType,
} from "@interface";
import type { CancelOrderRequestType } from "@interface/common/types";
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
): Promise<CancelOrderResponseType> => {
  const { data } = await sellerOrderApi.post(`/${paymentId}/cancel`, body);

  return data;
};

// PATCH: update order pickup ready
export const updatePickupReady = async (
  paymentId: string
): Promise<UpdateOrderAcceptType> => {
  const { data } = await sellerOrderApi.patch(`/${paymentId}/pickup-ready`);

  return data;
};

// GET: get order qr
export const GetOrderQr = async (paymentId: string): Promise<GetQrCodeType> => {
  const { data } = await sellerOrderApi.get(`/${paymentId}/qr`);

  return data;
};

// GET: get dashboard
export const GetDashboard = async (): Promise<DashboardResponseType> => {
  const { data } = await sellerOrderApi.get("/dashboard");

  return data;
};
