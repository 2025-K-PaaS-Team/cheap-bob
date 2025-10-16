import {
  SellerAgree,
  ConfirmOp,
  ConfirmStore,
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
  ConfirmPackage,
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
  ConfirmStore,
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
  ConfirmPackage,
  SuccessSetting,
];

export const notProgressBarPages: PageComponent[] = [
  SellerAgree,
  ConfirmStore,
  ConfirmPackage,
  SuccessSetting,
  ConfirmOp,
];

export const pkgPages: PageComponent[] = [
  RegisterPackageDesc,
  RegisterPackageNutrition,
  RegisterPackagePrice,
  RegisterPackageNum,
  ConfirmPackage,
];
