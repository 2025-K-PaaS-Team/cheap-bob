export const formatPhoneNumber = (input: string) => {
  const numbers = input.replace(/\D/g, "");

  if (numbers.length < 4) return numbers;
  if (numbers.length < 7) {
    return `${numbers.slice(0, 3)}-${numbers.slice(3)}`;
  }
  if (numbers.length <= 10) {
    return `${numbers.slice(0, 3)}-${numbers.slice(3, 6)}-${numbers.slice(6)}`;
  }
  return `${numbers.slice(0, 3)}-${numbers.slice(3, 7)}-${numbers.slice(
    7,
    11
  )}`;
};
