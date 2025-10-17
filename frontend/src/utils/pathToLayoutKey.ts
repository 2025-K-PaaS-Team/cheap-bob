import type { LayoutType, SellerLayoutType } from "@interface";

export const pathToLayoutKey = (path: string): LayoutType => {
  if (path === "/c") return "Home";
  if (path === "/c/signup") return "onBoarding";
  if (path.startsWith("/c/stores/") && path.endsWith("/payment"))
    return "Payment";
  if (path.startsWith("/c/stores/")) return "StoreDesc";
  if (path === "/c/stores") return "Home";
  if (path === "/c/favorite") return "FavStore";
  if (path === "/c/noti") return "Noti";
  if (path === "/c/my") return "My";
  if (path === "/c/order") return "Order";
  if (path === "/c/location") return "SetLoc";
  if (path === "/c/change/info") return "ChangeInfo";
  if (path === "/c/change/nutrition") return "ChangeNutrition";
  if (path === "/c/change/topping") return "ChangeTopping";
  if (path === "/c/change/allergy") return "ChangeAllergy";
  if (path === "/c/change/menu") return "ChangeMenu";
  return "default";
};

export const pathToSellerLayoutKey = (path: string): SellerLayoutType => {
  if (path.startsWith("/s/change/store")) return "changeStoreInfo";
  if (path.startsWith("/s/change/operation")) return "changeOperationInfo";
  if (path.startsWith("/s/change/package")) return "changePackageInfo";
  if (path === "/s/billing/change") return "billingChange";
  if (path === "/s/billing/history") return "billingHistory";
  return "default";
};
