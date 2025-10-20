export const getRoundedPrice = (price: number, sale: number) => {
  if (typeof price !== "number" || typeof sale !== "number") return 0;

  const discounted = (price * (100 - sale)) / 100;

  return Math.round(discounted / 100) * 100;
};
