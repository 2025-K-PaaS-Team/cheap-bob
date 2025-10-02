import type { SignupImageRequestType, SignupRequestType } from "@interface";
import { create } from "zustand";

type SignupState = {
  form: SignupRequestType;
  setForm: (form: Partial<SignupRequestType>) => void;
  resetForm: () => void;
};

type SignupImageState = {
  form: SignupImageRequestType;
  setForm: (form: Partial<SignupImageRequestType>) => void;
  resetForm: () => void;
};

export const useSignupStore = create<SignupState>((set) => ({
  form: {
    store_name: "",
    store_introduction: "",
    store_phone: "",
    sns_InfoType: { instagram: "", facebook: "", x: "", homepage: "" },
    address_InfoType: {
      postal_code: "",
      address: "",
      detail_address: "",
      sido: "",
      sigungu: "",
      bname: "",
      lat: "",
      lng: "",
    },
    operation_times: [],
    payment_InfoType: {
      portone_store_id: "",
      portone_channel_id: "",
      portone_secret_key: "",
    },
  },
  setForm: (form) => set((state) => ({ form: { ...state.form, ...form } })),
  resetForm: () =>
    set({
      form: {
        store_name: "",
        store_introduction: "",
        store_phone: "",
        sns_InfoType: { instagram: "", facebook: "", x: "", homepage: "" },
        address_InfoType: {
          postal_code: "",
          address: "",
          detail_address: "",
          sido: "",
          sigungu: "",
          bname: "",
          lat: "",
          lng: "",
        },
        operation_times: [],
        payment_InfoType: {
          portone_store_id: "",
          portone_channel_id: "",
          portone_secret_key: "",
        },
      },
    }),
}));

export const useSignupImageStore = create<SignupImageState>((set) => ({
  form: {
    store_id: "",
    images: [],
    total: 0,
  },
  setForm: (form) => set((state) => ({ form: { ...state.form, ...form } })),
  resetForm: () =>
    set({
      form: {
        store_id: "",
        images: [],
        total: 0,
      },
    }),
}));
