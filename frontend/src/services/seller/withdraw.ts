import type { WithdrawType } from "@interface";
import { sellerWithdrawApi } from "@services/client";

// POST: withdraw seller
export const WithdrawSeller = async (): Promise<WithdrawType> => {
  const { data } = await sellerWithdrawApi.post("");

  return data;
};

// DELETE: cancel withdraw
export const CancelWithdrawSeller = async (): Promise<WithdrawType> => {
  const { data } = await sellerWithdrawApi.delete("/cancel");

  return data;
};
