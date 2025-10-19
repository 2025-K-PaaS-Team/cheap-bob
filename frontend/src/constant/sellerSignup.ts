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
  RegisterStoreRepImg,
} from "@components/seller/signup";
import type { PageComponent } from "@interface";

export const pages: PageComponent[] = [
  // REGISTER STORE
  SellerAgree,
  RegisterName,
  RegisterDesc,
  RegisterNum,
  RegisterAddr,
  RegisterStoreRepImg,
  SuccessSetting, // page Idx 6
  // REGISTER OPERATION
  RegisterOpTime,
  RegisterPuTime,
  ConfirmOp,
  SuccessSetting, // page Idx 10
  // REGISTER PACKAGE
  RegisterPackageDesc,
  RegisterPackageNutrition,
  RegisterPackagePrice,
  RegisterPackageNum,
  ConfirmPackage,
  SuccessSetting, // page Idx 16
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
