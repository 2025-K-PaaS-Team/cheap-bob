export type PaymentStatusType = {
  status: "IDLE" | "PENDING" | "SUCCESS" | "FAILED";
  message?: string;
  code?: string;
};

export type ItemType = {
  id: number;
  name: string;
  price: number;
  currency: "KRW";
  currencyLabel: "원";
  img: string;
};

export type PaymentRequestType = {
  product_id: string;
  quantity: number;
};

export type PaymentResponseType = {
  payment_id: string;
  channel_id: string;
  store_id: string;
  total_amount: number;
};

export type PaymentConfirmType = {
  payment_id: string;
};
