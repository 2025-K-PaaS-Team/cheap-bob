import axios, { type AxiosInstance } from "axios";

const BASE = `${import.meta.env.VITE_API_BASE_URL}/api/v1`;

const attachInterceptors = (instance: AxiosInstance) => {
  instance.interceptors.request.use((config) => {
    const token = localStorage.getItem("accessToken");
    if (token) {
      config.headers = config.headers ?? {};
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  });
  return instance;
};

export const api = attachInterceptors(
  axios.create({
    baseURL: BASE,
    withCredentials: false,
    headers: { "Content-Type": "application/json" },
  })
);

export const sellerStoreApi = attachInterceptors(
  axios.create({
    baseURL: `${BASE}/seller/stores`,
    withCredentials: false,
    headers: { "Content-Type": "application/json" },
  })
);
