import type { LayoutType, SellerLayoutType } from "@interface";

export const pathToLayoutKey = (path: string): LayoutType => {
  if (path === "/c") return "Home";
  if (path === "/c/signup") return "onBoarding";
  if (path.startsWith("/c/stores/")) return "StoreDesc";
  if (path === "/c/stores") return "Home";
  if (path === "/c/favorite") return "FavStore";
  if (path === "/c/noti") return "Noti";
  if (path === "/c/my") return "My";
  if (path === "/c/order") return "Order";
  if (path === "/c/location") return "SetLoc";
  return "default";
};

export const pathToSellerLayoutKey = (path: string): SellerLayoutType => {
  if (path.startsWith("/s/change/store")) return "changeStoreInfo";
  if (path.startsWith("/s/change/operation")) return "changeOperationInfo";
  return "default";
};
