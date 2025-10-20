import type { TimeStamp } from "@interface/common/types";

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
  nearest_station: string;
  walking_time: number;
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

export type ImageInfoType = {
  image_id: string;
  image_url: string;
  is_main: boolean;
  display_order: number;
};

export type NutritionBase =
  | "diet"
  | "LCHF"
  | "protein"
  | "LSLS"
  | "balance"
  | "vegetarian";

export type NutritionInfoType = {
  id: number;
  nutrition_type: NutritionBase;
  created_at: TimeStamp;
};
