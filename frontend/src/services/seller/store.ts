import { sellerStoreApi, sellerStoreProfileApi } from "@services/client";

import type {
  SignupImageResponseType,
  SignupRequestType,
  SignupResponseType,
  StoreDetailType,
  UpdateStoreType,
} from "@interface";

// POST: register store
export const registerStore = async (
  body: SignupRequestType
): Promise<SignupResponseType> => {
  const { data } = await sellerStoreApi.post<SignupResponseType>(
    "/register",
    body
  );

  return data;
};

// POST: register store image
export const registerStoreImg = async (
  files: File[]
): Promise<SignupImageResponseType> => {
  const fd = new FormData();
  files.forEach((f) => fd.append("files", f));

  const { data } = await sellerStoreApi.post<SignupImageResponseType>(
    "/register/images",
    fd,
    {
      headers: { "Content-Type": undefined as any },
    }
  );
  return data;
};

// GET: get store detail
export const GetStoreDetail = async (): Promise<StoreDetailType> => {
  const { data } = await sellerStoreApi.get("");

  return data;
};

// PUT: update store name
export const UpdateStoreName = async (
  store_name: string
): Promise<UpdateStoreType> => {
  const { data } = await sellerStoreProfileApi.put("/name", { store_name });

  return data;
};
