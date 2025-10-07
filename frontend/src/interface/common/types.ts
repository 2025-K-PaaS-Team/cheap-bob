export type TimeStamp = string;

export type PaymentBaseType = {
  payment_id: string;
};

export type ProductBaseType = {
  product_id: string;
  product_name: string;
};

export type StoreBaseType = {
  store_id: string;
  store_name: string;
};

export type OrderStatusBaseType = {
  status:
    | "reservation"
    | "accepted"
    | "pickup_ready"
    | "completed"
    | "canceled";
  reservation_at: TimeStamp;
  accepted_at: TimeStamp;
  pickup_ready_at: TimeStamp;
  completed_at: TimeStamp;
  canceled_at: TimeStamp;
};

export type OrderWithTimestamp = OrderStatusBaseType & {
  [key: string]: TimeStamp | string;
};

export type OrderBaseType = PaymentBaseType &
  StoreBaseType &
  ProductBaseType &
  OrderWithTimestamp & {
    quantity: number;
    price: number;
  };

export type QrBaseType = {
  qr_data: string;
};

export type CoordBaseType = {
  lat: string;
  lng: string;
};
