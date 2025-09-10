import type { OrderBaseType, TimeStamp } from "@interface/common/types";

export type StoreBase = {
  store_id: string;
  store_name: string;
};

export type ProductDetailType = {
  product_id: string;
  product_name: string;
  stock: number;
  price: number;
};

export type StoreDetailType = StoreBase & {
  products: ProductDetailType[];
};

export type ProductBase = {
  product_name: string;
  price: number;
  sale: number;
};

export type ProductStockBase = ProductBase & {
  product_id: string;
  store_id: string;
  initial_stock: number;
  current_stock: number;
};

export type StoreProduct = Omit<ProductStockBase, "store_id">;

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
  ProductStockBase,
  "product_id" | "current_stock"
>;

export type ProductResponseType = ProductStockBase & {
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

export type UpdateProductStockRequestType = {
  stock: number;
};

export type GetStoreOrderType = {
  orders: OrderBaseType[];
  total: number;
};

export type UpdateOrderAcceptType = OrderBaseType;

export type CancelOrderRequestType = {
  reason: string;
};

export type CancelOrderResponseType = {
  payment_id: string;
  status: string;
  message: string;
  refunded_amount: number;
};


export type GetQrCodeType = {
  payment_id: string;
  qr_data: string;
  created_at: TimeStamp;
};
