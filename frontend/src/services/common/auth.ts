import type { UserRoleType } from "@interface";
import { authApi, userApi } from "./../client";

// POST: logout
export const PostLogout = async (state?: string) => {
  const { data } = await authApi.post(`/logout?state=${state}`);

  return data;
};

// GET: get user role
export const GetUserRole = async (): Promise<UserRoleType> => {
  const { data } = await userApi.get("");

  return data;
};
