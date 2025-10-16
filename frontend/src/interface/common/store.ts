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
  store_name: string;
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

// get store images
export type UpdateStoreImgType = {
  store_id: string;
  images: ImageInfoType[];
  total: number;
};

// get store operation
export type StoreOperationType = OperationTimeType[];

// change operation time
export type ChangeStoreOperationType = {
  operation_times: StoreOperationType;
};

// get operation reservation
export type OperationReservationBaseType = {
  modification_id: number;
  operation_id: number;
  day_of_week: number;
  new_open_time: TimeStamp;
  new_close_time: TimeStamp;
  new_pickup_start_time: TimeStamp;
  new_pickup_end_time: TimeStamp;
  new_is_open_enabled: boolean;
  created_at: TimeStamp;
};

export type OperationReservationType = {
  modifications: OperationReservationBaseType[];
};

export type StoreSearchBaseType = StoreDetailType & {
  is_favorite: boolean;
};

export type StoreSearchType = {
  stores: StoreSearchBaseType[];
  is_end: boolean;
};
