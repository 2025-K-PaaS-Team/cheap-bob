import type { NutritionBase } from "../common/base";

export type ProductBase = {
  product_name: string;
  description: string;
  price: number;
  sale: number;
};

export type ProductRequestType = ProductBase & {
  initial_stock: number;
  nutrition_types: string[];
};

export type ProductResponseType = ProductRequestType & {
  product_id: string;
  store_id: string;
  current_stock: number;
  version: number;
};

export type DashboardBaseType = {
  product_id: string;
  product_name: string;
  current_stock: number;
  initial_stock: number;
  purchased_stock: number;
  adjustment_stock: number;
};

export type DashboardResponseType = {
  items: DashboardBaseType[];
  total_items: number;
};

// get nutrition
export type NutritionType = {
  nutrition_types: NutritionBase[];
};

// get products
export type ProductBaseType = {
  product_id: string;
  store_id: string;
  product_name: string;
  description: string;
  initial_stock: number;
  current_stock: number;
  price: number;
  sale: number;
  version: number;
  nutrition_types: string[];
};

export type ProductType = {
  store_id: string;
  store_name: string;
  products: ProductBaseType[];
};
