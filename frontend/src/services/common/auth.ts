import { authApi } from "./../client";

// POST: logout
export const PostLogout = async (state?: string) => {
  const { data } = await authApi.post(`/logout?state=${state}`);

  return data;
};
