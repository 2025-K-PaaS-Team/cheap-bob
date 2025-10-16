import type { WithdrawType } from "@interface";
import { sellerWithdrawApi } from "@services/client";

// POST: withdraw seller
export const WithdrawSeller = async (): Promise<WithdrawType> => {
  const { data } = await sellerWithdrawApi.post("");

  return data;
};
