import type { TimeStamp } from "@interface/common/types";

export type CustomerDetailBaseType = {
  nickname: string;
  phone_number: number;
};

export type CustomerDetailType = CustomerDetailBaseType & {
  customer_email: string;
  created_at: TimeStamp;
  updated_at: TimeStamp;
};

export type CheckCustomerDetailType = {
  has_detail: boolean;
  detail: CustomerDetailType;
};

export type MenuBaseType = {
  menu_type: string;
};

export type PreferMenuBaseType = MenuBaseType & {
  id: number;
  created_at: TimeStamp;
};

export type PreferMenuType = {
  preferred_menus: PreferMenuBaseType[];
};
