import {
  SellerAgree,
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
  SuccessSetting,
  RegisterStoreRepImg,
  RegisterPackageName,
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
  SuccessSetting, // page Idx 9
  // REGISTER PACKAGE
  RegisterPackageName,
  RegisterPackageDesc,
  RegisterPackageNutrition,
  RegisterPackagePrice,
  RegisterPackageNum,
  SuccessSetting, // page Idx 15
];

export const notProgressBarPages: PageComponent[] = [
  SellerAgree,
  ConfirmStore,
  SuccessSetting,
];

export const pkgPages: PageComponent[] = [
  RegisterPackageName,
  RegisterPackageDesc,
  RegisterPackageNutrition,
  RegisterPackagePrice,
  RegisterPackageNum,
];
