import type { WithdrawType } from "@interface";
import { customerWithdrawApi } from "@services/client";

// POST: withdraw customer
export const WithdrawCustomer = async (): Promise<WithdrawType> => {
  const { data } = await customerWithdrawApi.post("");

  return data;
};

// DELETE: cancel withdraw
export const CancelWithdrawCustomer = async (
  state?: string
): Promise<WithdrawType> => {
  const { data } = await customerWithdrawApi.delete(`/cancel?state=${state}`);

  return data;
};
