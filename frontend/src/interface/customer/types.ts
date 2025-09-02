import type { OrderBaseType } from "@interface/common/types";

export type OrderDetailResponseType = OrderBaseType & {
  store_id: string;
  store_name: string;
};

export type OrdersResponseType = {
  orders: OrderDetailResponseType[];
  total: number;
};

export type OrderDeleteRequestType = {
  reason: string;
};

export type OrderDeleteResponseType = {
  payment_id: string;
  refunded_amount: number;
};
