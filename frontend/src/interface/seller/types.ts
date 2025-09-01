export type StoreRequestType = {
  store_name: string;
};

export type StoreResponseType = {
  store_id: string;
  store_name: string;
  seller_email: string;
  created_at: string;
};

export type ProductRequestType = {
  store_id: string;
  product_name: string;
  initial_stock: number;
  price: number;
  sale: number;
};

export type ProductResponseType = {
  product_id: string;
  store_id: string;
  product_name: string;
  initial_stock: number;
  current_stock: number;
  price: number;
  sale: number;
  version: number;
};

export type StorePaymentInfoRequestType = {
  portone_store_id: string;
  portone_channel_id: string;
  portone_secret_key: string;
};

export type StorePaymentInfoResponseType = {
  store_id: string;
  portone_store_id: string;
  portone_channel_id: string;
};
