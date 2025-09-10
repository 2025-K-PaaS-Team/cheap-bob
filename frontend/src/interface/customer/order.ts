import type { OrderBaseType } from "@interface/common/types";

export type OrderResponseType = {
  orders: OrderBaseType[];
  total: number;
};

export type OrderDetailResponseType = OrderBaseType & {
  unit_price: number;
  discount_rate: number;
};

export type OrderDeleteRequestType = {
  reason: string;
};

export type OrderDeleteResponseType = {
  payment_id: string;
  refunded_amount: number;
};
