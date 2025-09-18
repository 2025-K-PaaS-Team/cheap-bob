import type { LayoutType } from "@interface";

export const pathToLayoutKey = (path: string): LayoutType => {
  if (path === "/c") return "Home";
  if (path === "/c/signup") return "onBoarding";
  if (path.startsWith("/c/stores/")) return "StoreDesc";
  if (path === "/c/stores") return "Search";
  if (path === "/c/my") return "My";
  return "default";
};
