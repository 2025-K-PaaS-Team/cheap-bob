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

// GET: get product
export const GetProduct = async (
  product_id: string
): Promise<ProductResponseType> => {
  const { data } = await sellerProductApi.get(`/${product_id}`);

  return data;
};

// PUT: update product
export const UpdateProduct = async (
  product_id: string,
  product: ProductBase
): Promise<ProductResponseType> => {
  const { data } = await sellerProductApi.put(`/${product_id}`, product);

  return data;
};

// POST: add product nutrition
export const AddPkgNutrition = async (
  product_id: string,
  types: string[]
): Promise<ProductResponseType> => {
  const { data } = await sellerProductApi.post(`/${product_id}/nutrition`, {
    nutrition_types: types,
  });
  return data;
};

// DELETE: delete product nutrition
export const DeletePkgNutrition = async (
  product_id: string,
  types: string[]
): Promise<ProductResponseType> => {
  const { data } = await sellerProductApi.delete(`/${product_id}/nutrition`, {
    data: { nutrition_types: types },
  });
  return data;
};
