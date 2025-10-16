export const getTitleByKey = <T extends { key: string; title: string }>(
  key: string,
  list: T[],
  defaultTitle = ""
): string => {
  return list.find((item) => item.key === key)?.title ?? defaultTitle;
};
