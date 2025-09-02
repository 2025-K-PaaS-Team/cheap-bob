import type {
  ProductBase,
  ProductRequestType,
  ProductResponseType,
  UpdateProductStockRequestType,
} from "@interface";
import { sellerProductApi } from "@services/client";

// POST: create product
export const createProduct = async (
  body: ProductRequestType
): Promise<ProductResponseType> => {
  const { data } = await sellerProductApi.post<ProductResponseType>("", body);
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
export const deleteProduct = async (productId: string): Promise<void> => {
  await sellerProductApi.delete<void>(`/${productId}`);
};

// PATCH: update product stock
export const updateProductStock = async (
  productId: string,
  body: UpdateProductStockRequestType
): Promise<ProductResponseType> => {
  const { data } = await sellerProductApi.patch<ProductResponseType>(
    `/${productId}/stock`,
    body
  );

  return data;
};
