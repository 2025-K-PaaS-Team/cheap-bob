export type OrderDetailResponseType = {
  payment_id: string;
  product_id: string;
  product_name: string;
  store_id: string;
  store_name: string;
  quantity: number;
  price: number;
  status: string;
  created_at: string;
  confirmed_at: string;
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
