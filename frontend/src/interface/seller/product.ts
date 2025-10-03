export type ProductBase = {
  product_name: string;
  description: string;
  price: number;
  sale: number;
};

export type NutritionBase =
  | "diet"
  | "LCHF"
  | "protein"
  | "LSLS"
  | "balance"
  | "vegetarian";

export type ProductRequestType = ProductBase & {
  initial_stock: number;
  nutrition_types: NutritionBase[];
};

export type ProductResponseType = ProductRequestType & {
  product_id: string;
  store_id: string;
  current_stock: number;
  version: number;
};
