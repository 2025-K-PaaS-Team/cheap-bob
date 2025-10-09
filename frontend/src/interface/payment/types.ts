export type PaymentStatusType = {
  status: "IDLE" | "PENDING" | "SUCCESS" | "FAILED";
  message?: string;
  code?: string;
};

export type ItemType = {
  id: string;
  name: string;
  price: number;
  currency: "KRW";
  currencyLabel: "원";
};

export type PaymentRequestType = {
  product_id: string;
  quantity: number;
};

export type PaymentBaseType = {
  payment_id: string;
};

export type PaymentResponseType = PaymentBaseType & {
  channel_id: string;
  store_id: string;
  total_amount: number;
};

export type PaymentConfirmType = PaymentBaseType;
