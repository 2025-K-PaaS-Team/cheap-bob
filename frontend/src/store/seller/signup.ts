import type {
  Offset,
  SignupImageRequestType,
  SignupRequestType,
} from "@interface";
import { create } from "zustand";

type SignupState = {
  form: SignupRequestType;
  setForm: (
    form:
      | Partial<SignupRequestType>
      | ((prev: SignupRequestType) => Partial<SignupRequestType>)
  ) => void;
  resetForm: () => void;
  // time offset
  pickupStartOffset: Offset;
  pickupDiscardOffset: Offset;
  setPickupStartOffset: (hour: number, min: number) => void;
  setPickupDiscardOffset: (hour: number, min: number) => void;
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

  setForm: (update) =>
    set((state) => {
      const patch = typeof update === "function" ? update(state.form) : update;
      return { form: { ...state.form, ...patch } };
    }),

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
      pickupStartOffset: { hour: 0, min: 0 },
      pickupDiscardOffset: { hour: 0, min: 0 },
    }),

  // initial offset value
  pickupStartOffset: { hour: 0, min: 0 },
  pickupDiscardOffset: { hour: 0, min: 0 },

  setPickupStartOffset: (hour, min) =>
    set(() => ({ pickupStartOffset: { hour, min } })),
  setPickupDiscardOffset: (hour, min) =>
    set(() => ({ pickupDiscardOffset: { hour, min } })),
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
