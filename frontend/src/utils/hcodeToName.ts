import { codeToName } from "@constant";

export const hcodeToName = (code: string): string => {
  const key = Number(code);
  if (Number.isNaN(key)) return "";
  return codeToName[key] || "";
};
