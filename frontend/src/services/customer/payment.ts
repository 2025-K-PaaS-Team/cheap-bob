import type { PaymentRequestType, PaymentResponseType } from "@interface";
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
