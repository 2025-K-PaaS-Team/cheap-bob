import type {
  CheckCustomerDetailType,
  CustomerDetailBaseType,
  CustomerDetailType,
} from "@interface";
import { customerProfileApi } from "@services/client";

// GET: check customer detail(2-step user info)
export const CheckCustomerDetail =
  async (): Promise<CheckCustomerDetailType> => {
    const { data } = await customerProfileApi.get("/check");

    return data;
  };

// POST: create customer detail
export const CreateCustomerDetail = async (
  body: CustomerDetailBaseType
): Promise<CustomerDetailType> => {
  const { data } = await customerProfileApi.post("/profile/detail", body);

  return data;
};
