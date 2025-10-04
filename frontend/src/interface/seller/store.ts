import type { TimeStamp } from "@interface/common/types";
import type {
  AddressInfoType,
  ImageInfoType,
  OperationTimeType,
  SnsInfoType,
  StoreInfoType,
} from "./base";
import type { ProductResponseType } from "./product";

export type StoreAddrDetailType = AddressInfoType & {
  store_id: string;
};

export type StoreOperationTimeDetailType = OperationTimeType & {
  operation_id: number;
  store_id: string;
  is_currently_open: boolean;
  updated_at: TimeStamp;
};

export type StoreDetailType = StoreInfoType & {
  store_id: string;
  seller_email: string;
  created_at: TimeStamp;
  address: StoreAddrDetailType;
  sns: SnsInfoType;
  operation_times: StoreOperationTimeDetailType[];
  images: ImageInfoType[];
  products: ProductResponseType[];
};

// update store name, introduction, phone
export type UpdateStoreType = StoreInfoType & {
  store_id: string;
};

// update store sns
export type UpdateStoreSnsType = SnsInfoType & {
  store_id: string;
};

// update store address
export type UpdateStoreAddrType = AddressInfoType & {
  store_id: string;
};
