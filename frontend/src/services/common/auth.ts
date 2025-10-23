import { authApi } from "./../client";

// POST: logout
export const PostLogout = async () => {
  const { data } = await authApi.post("/logout");

  return data;
};
