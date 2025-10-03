import type { JSX } from "react";
import type { ProductRequestType } from "./product";

export interface SellerSignupProps {
  pageIdx: number;
  setPageIdx: React.Dispatch<React.SetStateAction<number>>;
}

export interface SellerSignupPkgProps extends SellerSignupProps {
  pkg: ProductRequestType;
  setPkg: React.Dispatch<React.SetStateAction<ProductRequestType>>;
}

export type PageComponent =
  | ((props: SellerSignupProps) => JSX.Element)
  | ((props: SellerSignupPkgProps) => JSX.Element);

export type StoreInfoType = {
  store_name: string;
  store_introduction: string;
  store_phone: string;
};

export type SnsInfoType = {
  instagram?: string;
  facebook?: string;
  x?: string;
  homepage?: string;
};

export type AddressInfoType = {
  postal_code: string;
  address: string;
  detail_address: string;
  sido: string;
  sigungu: string;
  bname: string;
  lat: string;
  lng: string;
};

export type OperationTimeType = {
  day_of_week: number;
  open_time: string;
  pickup_start_time: string;
  pickup_end_time: string;
  close_time: string;
  is_open_enabled: boolean;
};

export type PaymentInfoType = {
  portone_store_id: string;
  portone_channel_id: string;
  portone_secret_key: string;
};

export type SignupRequestType = StoreInfoType & {
  sns_info: SnsInfoType;
  address_info: AddressInfoType;
  operation_times: OperationTimeType[];
  payment_info: PaymentInfoType;
};

export type SignupResponseType = {
  store_id: string;
  store_name: string;
  message: string;
};

export type ImagesType = {
  file: File;
  preview: string;
};

export type SignupImageRequestType = {
  images: ImagesType[];
};

export type SignupImageBaseType = {
  image_id: string;
  image_url: string;
  is_main: boolean;
  display_order: number;
};

export type SignupImageResponseType = {
  store_id: string;
  images: SignupImageBaseType[];
  total: number;
};

export type Offset = { hour: number; min: number };
