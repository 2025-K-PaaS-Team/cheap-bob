import type { JSX } from "react";

import type {
  AddressInfoType,
  ImageInfoType,
  OperationTimeType,
  PaymentInfoType,
  SnsInfoType,
  StoreInfoType,
} from "../common/base";
import type { ProductRequestType } from "@interface/common/product";

export interface SellerSignupPkgProps {
  pkg: ProductRequestType;
  setPkg: React.Dispatch<React.SetStateAction<ProductRequestType>>;
}

export type PageComponent = (props: SellerSignupPkgProps) => JSX.Element;

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

export type SignupImageResponseType = {
  store_id: string;
  images: ImageInfoType[];
  total: number;
};

export type Offset = { hour: number; min: number };
