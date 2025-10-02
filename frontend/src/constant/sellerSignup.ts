import {
  SellerAgree,
  ConfirmOp,
  ConfirmSetting,
  RegisterAddr,
  RegisterDesc,
  RegisterName,
  RegisterNum,
  RegisterOpTime,
  RegisterPackageDesc,
  RegisterPackageNum,
  RegisterPackageNutrition,
  RegisterPackagePrice,
  RegisterPuTime,
  SuccessSetting,
} from "@components/seller/signup";
import type { PageComponent } from "@interface";

export const pages: PageComponent[] = [
  // REGISTER STORE
  SellerAgree,
  RegisterName,
  RegisterDesc,
  RegisterAddr,
  RegisterNum,
  ConfirmSetting,
  SuccessSetting,
  // REGISTER OPERATION
  RegisterOpTime,
  RegisterPuTime,
  ConfirmOp,
  SuccessSetting,
  // REGISTER PACKAGE
  RegisterPackageDesc,
  RegisterPackageNutrition,
  RegisterPackagePrice,
  RegisterPackageNum,
  ConfirmSetting,
  SuccessSetting,
];

export const notProgressBarPages: PageComponent[] = [
  SellerAgree,
  ConfirmSetting,
  SuccessSetting,
  ConfirmOp,
];

export const pkgPages: PageComponent[] = [
  RegisterPackageDesc,
  RegisterPackageNutrition,
  RegisterPackagePrice,
  RegisterPackageNum,
];
