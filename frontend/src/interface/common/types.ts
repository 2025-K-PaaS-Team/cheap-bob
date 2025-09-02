export type TimeStamp = string;

export type OrderBaseType = {
  payment_id: string;
  product_id: string;
  product_name: string;
  quantity: number;
  price: number;
  status: string;
  created_at: TimeStamp;
  confirmed_at: TimeStamp;
};
