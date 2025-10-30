import type {
  DashboardResponseType,
  GetQrCodeType,
  GetStoreOrderType,
  OrderResponseType,
  UpdateOrderAcceptType,
} from "@interface";
import { sellerOrderApi } from "@services/client";

// GET: get store orders
export const getStoreOrder = async (): Promise<OrderResponseType> => {
  const { data } = await sellerOrderApi.get("");

  return data;
};

// GET: get store today orders
export const getStoreTodayOrder = async (): Promise<OrderResponseType> => {
  const { data } = await sellerOrderApi.get("/today");

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
export const cancelOrder = async (paymentId: string, reason: string) => {
  const { data } = await sellerOrderApi.delete(`${paymentId}/cancel`, {
    data: {
      reason: reason,
    },
  });

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
