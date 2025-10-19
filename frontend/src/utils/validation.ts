export const validationRules = {
  storeName: {
    minLength: 1,
    maxLength: 20,
    errorMessage: "매장 이름은 1~20자여야 합니다.",
  },
  storeDesc: {
    minLength: 1,
    maxLength: 100,
    errorMessage: "매장 설명은 1~100자여야 합니다.",
  },
  storeAddr: {
    errorMessage: "매장 주소를 설정해 주세요.",
  },
  storePhone: {
    pattern: /^0\d{1,2}\d{3,4}\d{4}$/,
    errorMessage: "01012345678 형식으로 입력해 주세요.",
  },
  packageName: {
    minLength: 1,
    maxLength: 20,
    errorMessage: "패키지 이름은 1~20자여야 합니다.",
  },
  packageDesc: {
    minLength: 1,
    maxLength: 100,
    errorMessage: "패키지 설명은 1~100자여야 합니다.",
  },
  packageSelect: {
    minSelect: 1,
    maxSelect: 3,
    errorMessage: "영양 정보는 최대 3개까지 선택 가능합니다.",
  },
  packagePrice: {
    minPrice: 1000,
    errorMessage: "패키지의 가격은 1000원 이상이어야 합니다.",
  },
  packageStock: {
    minStock: 1,
    errorMessage: "패키지의 초기 수량은 양수여야 합니다.",
  },
};

export const validateLength = (value: string, min: number, max: number) =>
  value?.length >= min && value?.length <= max;

export const validatePattern = (value: string, pattern: RegExp) =>
  pattern?.test(value);

export const validateSelect = (value: number, min: number, max: number) =>
  value >= min && value <= max;

export const validateNum = (value: number, min: number) => value >= min;

export const validateUrl = (url: string) => {
  if (!url) return true;
  try {
    const normalized = normalizeUrl(url) ?? "";
    const urlPattern = /^(https?:\/\/)([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})(\/\S*)?$/;
    return urlPattern.test(normalized);
  } catch {
    return false;
  }
};

export const normalizeUrl = (raw?: string): string | undefined => {
  const s = (raw ?? "").trim();
  if (!s) return undefined;
  const withScheme = /^https?:\/\//i.test(s) ? s : `https://${s}`;
  try {
    new URL(withScheme);
    return withScheme;
  } catch {
    return undefined;
  }
};
