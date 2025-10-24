import {
  sellerStoreApi,
  sellerStoreImgApi,
  sellerStoreProfileApi,
  sellerStoreSettingsApi,
  sellerStoreSnsApi,
} from "@services/client";

import type {
  AddressInfoType,
  ChangeStoreOperationType,
  ImageInfoType,
  OperationReservationType,
  RegisterPaymentType,
  SignupImageResponseType,
  SignupRequestType,
  SignupResponseType,
  SnsInfoType,
  StoreDetailType,
  StoreOperationType,
  StorePaymentResponseType,
  StorePaymentType,
  UpdateStoreAddrType,
  UpdateStoreImgType,
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

// GET: check payment info
export const CheckPaymentInfo = async () => {
  const { data } = await sellerStoreApi.get("/register/payment");

  return data;
};

// GET: get store detail
export const GetStoreDetail = async (): Promise<StoreDetailType> => {
  const { data } = await sellerStoreApi.get("");

  return data;
};

// PATCH: close store
export const CloseStore = async () => {
  const { data } = await sellerStoreApi.patch("/close");

  return data;
};

// GET: Get seller profile all
export const GetSellerEmail = async () => {
  const { data } = await sellerStoreProfileApi.get("/me");

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

// PUT: update store address
export const UpdateStoreAddr = async (
  addr: AddressInfoType
): Promise<UpdateStoreAddrType> => {
  const { data } = await sellerStoreSettingsApi.put("/address", addr);

  return data;
};

// GET: get store images
export const GetStoreImg = async (): Promise<UpdateStoreImgType> => {
  const { data } = await sellerStoreImgApi.get("", {
    headers: { "Cache-Control": "no-cache" },
  });

  return data;
};

// POST: add store images
export const AddStoreImg = async (
  files: File[]
): Promise<UpdateStoreImgType> => {
  const fd = new FormData();
  files.forEach((f) => fd.append("files", f));

  const { data } = await sellerStoreImgApi.post<UpdateStoreImgType>("", fd, {
    headers: { "Content-Type": undefined as any },
  });
  return data;
};

// DELETE: delete store image
export const DeleteStoreImg = async (image_id: string) => {
  const { data } = await sellerStoreImgApi.delete(`/${image_id}`);

  return data;
};

// PUT: change main image
export const ChangeStoreMainImg = async (
  image_id: string
): Promise<ImageInfoType> => {
  const { data } = await sellerStoreImgApi.put(`/main/${image_id}`);

  return data;
};

// GET: get store operation
export const GetStoreOperation = async (): Promise<StoreOperationType> => {
  const { data } = await sellerStoreSettingsApi.get("/operation");

  return data;
};

// GET: get store operation reservation
export const GetStoreOpReservation =
  async (): Promise<OperationReservationType> => {
    const { data } = await sellerStoreSettingsApi.get("/operation/reservation");

    return data;
  };

// POST: create operation reservation
export const CreateOperationReservation = async (
  res: ChangeStoreOperationType
): Promise<OperationReservationType> => {
  const { data } = await sellerStoreSettingsApi.post(
    "/operation/reservation",
    res
  );

  return data;
};

// PATCH: Update store payment
export const UpdateStorePayment = async (
  body: StorePaymentType
): Promise<StorePaymentResponseType> => {
  const { data } = await sellerStoreSettingsApi.put("/payment", body);

  return data;
};

// POST: Register Payment info
export const RegisterPayment = async (body: RegisterPaymentType) => {
  const { data } = await sellerStoreApi.post("/register/payment", body);

  return data;
};
