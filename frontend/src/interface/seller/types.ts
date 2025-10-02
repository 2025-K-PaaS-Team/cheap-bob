import type {
  OrderBaseType,
  QrBaseType,
  StoreBaseType,
  TimeStamp,
} from "@interface/common/types";

export interface SellerSignupProps {
  pageIdx: number;
  setPageIdx: React.Dispatch<React.SetStateAction<number>>;
}

export type ProductDetailType = {
  product_id: string;
  product_name: string;
  stock: number;
  price: number;
};

export type StoreDetailType = StoreBaseType & {
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

export type StoreResponseType = StoreBaseType & {
  seller_email: string;
  created_at: TimeStamp;
};

export type StoreWithProductResponseType = StoreBaseType & {
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

export type CancelOrderResponseType = {
  payment_id: string;
  status: string;
  message: string;
  refunded_amount: number;
};

export type GetQrCodeType = QrBaseType & {
  payment_id: string;
  created_at: TimeStamp;
};

export type CoorBaseType = {
  lng: string;
  lat: string;
};

export type MapBaseType = {
  postal_code: any;
  address: string;
  detail_address: string;
  sido: string;
  sigungu: string;
  bname: string;
  lng: string;
  lat: string;
};
