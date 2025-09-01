import type { ProductRequestType, ProductResponseType } from "@interface";
import { sellerProductApi } from "@services/client";

// POST: create product
export const createProduct = async (
  body: ProductRequestType
): Promise<ProductResponseType> => {
  const { data } = await sellerProductApi.post<ProductResponseType>("", body);
  return data;
};
