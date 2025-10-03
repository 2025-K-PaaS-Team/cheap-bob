import type {
  ProductBase,
  ProductRequestType,
  ProductResponseType,
} from "@interface";
import { sellerProductApi } from "@services/client";

// POST: create product
export const createProduct = async (
  body: ProductRequestType
): Promise<ProductResponseType> => {
  const { data } = await sellerProductApi.post<ProductResponseType>(
    "/register",
    body
  );
  return data;
};

// PUT: update product price
export const updateProductPrice = async (
  productId: string,
  body: ProductBase
): Promise<ProductResponseType> => {
  const { data } = await sellerProductApi.put<ProductResponseType>(
    `/${productId}`,
    body
  );

  return data;
};

// DELETE: delete product
// export const deleteProduct = async (productId: string): Promise<void> => {
//   await sellerProductApi.delete<void>(`/${productId}`);
// };

// PATCH: Increase product stock
export const IncreaseProductStock = async (
  productId: string
): Promise<ProductResponseType> => {
  const { data } = await sellerProductApi.patch<ProductResponseType>(
    `/${productId}/stock/up`
  );

  return data;
};

// PATCH: Decrease product stock
export const DecreaseProductStock = async (
  productId: string
): Promise<ProductResponseType> => {
  const { data } = await sellerProductApi.patch<ProductResponseType>(
    `/${productId}/stock/down`
  );

  return data;
};
