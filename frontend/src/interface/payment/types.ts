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
