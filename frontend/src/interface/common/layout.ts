import type { layoutMap, sellerLayoutMap } from "@constant";

export type LayoutType = keyof typeof layoutMap;
// "onBoarding" | "Home" | "SetLoc" | ... | "My"

export type LayoutConfig = (typeof layoutMap)[LayoutType];
// {
//   back: boolean;
//   title: string;
//   loc: boolean;
//   heart: boolean;
//   noti: boolean;
// }

export type SellerLayoutType = keyof typeof sellerLayoutMap;
export type SellerLayoutConfig = (typeof sellerLayoutMap)[SellerLayoutType];
