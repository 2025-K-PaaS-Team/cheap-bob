import { layoutMap, sellerLayoutMap } from "@constant";

export const getLayoutByPath = (path: string) => {
  const found = layoutMap.find((layout) =>
    layout.paths.some((p) =>
      typeof p === "string" ? p === path : p.test(path)
    )
  );

  return found || layoutMap.find((l) => l.key === "default")!;
};

export const getSellerLayoutByPath = (path: string) => {
  const found = sellerLayoutMap.find((layout) =>
    layout.paths.some((p) =>
      typeof p === "string" ? p === path : p.test(path)
    )
  );
  return found || sellerLayoutMap.find((l) => l.key === "default")!;
};
