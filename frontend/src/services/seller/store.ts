import {
  sellerStoreApi,
  sellerStoreProfileApi,
  sellerStoreSnsApi,
} from "@services/client";

import type {
  SignupImageResponseType,
  SignupRequestType,
  SignupResponseType,
  SnsInfoType,
  StoreDetailType,
  UpdateStoreSnsType,
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

// PUT: update store description
export const UpdateStoreDesc = async (
  store_introduction: string
): Promise<UpdateStoreType> => {
  const { data } = await sellerStoreProfileApi.put("/introduction", {
    store_introduction,
  });

  return data;
};

// PUT: update store phone
export const UpdateStorePhone = async (
  store_phone: string
): Promise<UpdateStoreType> => {
  const { data } = await sellerStoreProfileApi.put("/phone", {
    store_phone,
  });

  return data;
};

// PUT: update store sns
export const UpdateStoreSns = async (
  sns: SnsInfoType
): Promise<UpdateStoreSnsType> => {
  const { data } = await sellerStoreSnsApi.put("", sns);

  return data;
};
