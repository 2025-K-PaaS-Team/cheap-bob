import type { LayoutType } from "@interface";

export const pathToLayoutKey = (path: string): LayoutType => {
  if (path === "/c") return "Home";
  if (path === "/c/signup") return "onBoarding";
  if (path.startsWith("/c/stores/")) return "StoreDesc";
  if (path === "/c/stores") return "Home";
  if (path === "/c/favorite") return "FavStore";
  if (path === "/c/noti") return "Noti";
  if (path === "/c/my") return "My";
  if (path === "/c/order") return "Order";
  return "default";
};
