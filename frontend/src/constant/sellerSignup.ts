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

export const pages = [
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

export const notProgressBarPages = [
  SellerAgree,
  ConfirmSetting,
  SuccessSetting,
  ConfirmOp,
];
