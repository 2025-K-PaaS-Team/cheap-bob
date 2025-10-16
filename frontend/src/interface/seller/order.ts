import type { TimeStamp } from "@interface/common/types";

export type OrderStatusType =
  | "reservation"
  | "accept"
  | "completed"
  | "canceled";

export type OrderBaseType = {
  payment_id: string;
  customer_id: string;
  customer_nickname: string;
  customer_phone_number: string;
  product_id: string;
  product_name: string;
  store_id: string;
  store_name: string;
  quantity: number;
  price: number;
  sale: number;
  total_amount: number;
  status: OrderStatusType;
  reservation_at: TimeStamp;
  accepted_at: TimeStamp;
  completed_at: TimeStamp;
  canceled_at: TimeStamp;
  cancel_reason: string;
  preferred_menus: string[];
  nutrition_types: string[];
  allergies: string[];
  topping_types: string[];
};

export type OrderResponseType = {
  orders: OrderBaseType[];
  total: number;
};

export type CancelOrderRequestType = {
  reason: string;
};
