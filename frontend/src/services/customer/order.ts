import type {
  OrderDeleteResponseType,
  OrderDetailResponseType,
  OrderResponseType,
} from "@interface/customer/order";
import { customerOrderApi } from "@services/client";

// GET: get order history
export const getOrders = async (): Promise<OrderResponseType> => {
  const { data } = await customerOrderApi.get("");

  return data;
};

// GET: get current order
export const getCurrentOrders = async (): Promise<OrderResponseType> => {
  const { data } = await customerOrderApi.get("/current");
  return data;
};

// GET: get order detail
export const getOrderDetail = async (
  paymentId: string
): Promise<OrderDetailResponseType> => {
  const { data } = await customerOrderApi.get(`/${paymentId}`);

  return data;
};

// DELETE: delete order
export const deleteOrder = async (
  paymentId: string
): Promise<OrderDeleteResponseType> => {
  const { data } = await customerOrderApi.delete(`/${paymentId}`);

  return data;
};
