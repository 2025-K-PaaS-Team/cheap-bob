import type { SettlementType, SettlementWeekType } from "@interface";
import { sellerSettlementApi } from "@services/client";

// GET: get store settlement
export const GetStoreSettlement = async (
  start: string,
  end: string
): Promise<SettlementType> => {
  const { data } = await sellerSettlementApi.get("", {
    params: { start_date: start, end_date: end },
  });

  return data;
};

// GET: get store weekly settlement
export const GetStoreWeekSettlement = async (): Promise<SettlementWeekType> => {
  const { data } = await sellerSettlementApi.get("/weekly-revenue");

  return data;
};
