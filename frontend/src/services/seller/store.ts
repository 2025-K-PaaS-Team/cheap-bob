import { sellerStoreApi } from "@services/client";

import type {
  SignupImageResponseType,
  SignupRequestType,
  SignupResponseType,
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
    fd
  );
  return data;
};
