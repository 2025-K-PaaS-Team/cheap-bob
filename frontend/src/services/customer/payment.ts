import type {
  PaymentConfirmType,
  PaymentRequestType,
  PaymentResponseType,
} from "@interface";
import { customerPaymentApi } from "@services/client";

// POST: init payment
export const initPayment = async (
  body: PaymentRequestType
): Promise<PaymentResponseType> => {
  const { data } = await customerPaymentApi.post<PaymentResponseType>(
    "/init",
    body
  );

  return data;
};

// POST: confirm payment
export const confrimPayment = async (
  body: PaymentConfirmType
): Promise<PaymentConfirmType> => {
  const { data } = await customerPaymentApi.post<PaymentConfirmType>(
    "/confirm",
    body
  );

  return data;
};

// DELETE: cancel payment
export const cancelPayment = async (
  paymentId: string
): Promise<PaymentConfirmType> => {
  const { data } = await customerPaymentApi.delete<PaymentConfirmType>(
    `/cancel/${paymentId}`
  );

  return data;
};
