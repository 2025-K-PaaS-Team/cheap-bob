export interface SellerSignupProps {
  pageIdx: number;
  setPageIdx: React.Dispatch<React.SetStateAction<number>>;
}

export type StoreInfoType = {
  store_name: string;
  store_introduction: string;
  store_phone: string;
};

export type SnsInfoType = {
  instagram: string;
  facebook: string;
  x: string;
  homepage: string;
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

export type OperationTime = {
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
  sns_InfoType: SnsInfoType;
  address_InfoType: AddressInfoType;
  operation_times: OperationTime[];
  payment_InfoType: PaymentInfoType;
};
