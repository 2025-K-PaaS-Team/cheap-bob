import type {
  OrderBaseType,
  QrBaseType,
  TimeStamp,
} from "@interface/common/types";

export type ProductDetailType = {
  product_id: string;
  product_name: string;
  stock: number;
  price: number;
};

// export type StoreDetailType = StoreBaseType & {
//   products: ProductDetailType[];
// };

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

export type WithdrawType = {
  message: string;
  access_token: string;
};
