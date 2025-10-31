import type { TimeStamp } from "@interface/common/types";
import type { OrderBaseType } from "@interface";

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

export type AlarmBaseType = {
  payment_id: string;
  order_time: TimeStamp;
  quantity: number;
  price: number;
  sale: number;
  total_amount: number;
  status: string;
  store_name: string;
  product_name: string;
  pickup_start_time: string;
  pickup_end_time: string;
};
