import type { OrderBaseType, QrBaseType } from "@interface/common/types";
import type {
  // OrderDeleteResponseType,
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
  const { data } = await customerOrderApi.get("/today");
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
export const deleteOrder = async (paymentId: string) => {
  const { data } = await customerOrderApi.delete(`/${paymentId}/cancel`, {
    data: {
      reason: "형식을 맞추기 위한 reason",
    },
  });

  return data;
};

// PATCH: patch pickup complete
export const completePickup = async (
  paymentId: string,
  body: QrBaseType
): Promise<OrderBaseType> => {
  const { data } = await customerOrderApi.patch(`/${paymentId}/complete`, body);

  return data;
};
