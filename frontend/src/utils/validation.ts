export const validationRules = {
  storeName: {
    minLength: 1,
    maxLength: 7,
    errorMessage: "매장 이름은 1~7자여야 합니다.",
  },
  storeDesc: {
    minLength: 1,
    maxLength: 100,
    errorMessage: "매장 설명은 1~100자여야 합니다.",
  },
  storeAddr: {
    errorMessage: "매장 주소를 설정해 주세요.",
  },
  phone: {
    pattern: /^0\d{1,2}-\d{3,4}-\d{4}$/,
    errorMessage: "전화번호 형식이 올바르지 않습니다.",
  },
  password: { minLength: 8, errorMessage: "비밀번호는 8자 이상이어야 합니다." },
};

export const validateLength = (value: string, min: number, max: number) =>
  value.length >= min && value.length <= max;

export const validatePattern = (value: string, pattern: RegExp) =>
  pattern.test(value);
