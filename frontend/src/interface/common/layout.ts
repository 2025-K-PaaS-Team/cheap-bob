import type { layoutMap } from "@constant";

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
