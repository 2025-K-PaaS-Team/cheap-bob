import type { WithdrawType } from "@interface";
import { customerWithdrawApi } from "@services/client";

// POST: withdraw customer
export const WithdrawCustomer = async (): Promise<WithdrawType> => {
  const { data } = await customerWithdrawApi.post("");

  return data;
};

// DELETE: cancel withdraw
export const CancelWithdrawCustomer = async (): Promise<WithdrawType> => {
  const { data } = await customerWithdrawApi.delete("/cancel");

  return data;
};
