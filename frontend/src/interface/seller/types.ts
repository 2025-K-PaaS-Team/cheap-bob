import type { TimeStamp } from "@interface/common/types";

export type StoreBase = {
  store_id: string;
  store_name: string;
};

export type ProductBase = {
  product_id: string;
  store_id: string;
  product_name: string;
  initial_stock: number;
  current_stock: number;
  price: number;
  sale: number;
};

export type StoreProduct = Omit<ProductBase, "store_id">;

export type StoreRequestType = {
  store_name: string;
};

export type StoreResponseType = StoreBase & {
  seller_email: string;
  created_at: TimeStamp;
};

export type StoreWithProductResponseType = StoreBase & {
  products: StoreProduct[];
  total: number;
};

export type ProductRequestType = Omit<
  ProductBase,
  "product_id" | "current_stock"
>;

export type ProductResponseType = ProductBase & {
  version: number;
};

export type PaymentBase = {
  portone_store_id: string;
  portone_channel_id: string;
};

export type StorePaymentInfoRequestType = PaymentBase & {
  portone_secret_key: string;
};

export type StorePaymentStatusType = {
  info_status: boolean;
};

export type StorePaymentInfoResponseType = PaymentBase & {
  store_id: string;
};
