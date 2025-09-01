import api from "./client";

export type CreateStoreRequest = {
  store_name: string;
};

export type CreateStoreResponse = {
  store_id: string;
  store_name: string;
  seller_email: string;
  created_at: string;
};

const createStore = async (
  body: CreateStoreRequest
): Promise<CreateStoreResponse> => {
  const { data } = await api.post<CreateStoreResponse>(
    "/api/v1/seller/stores",
    body
  );

  return data;
};

export default createStore;
