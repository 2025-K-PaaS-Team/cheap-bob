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
  SellerAgree,
  RegisterName,
  RegisterDesc,
  RegisterAddr,
  RegisterNum,
  ConfirmSetting,
  SuccessSetting,
  RegisterOpTime,
  RegisterPuTime,
  ConfirmOp,
  SuccessSetting,
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
