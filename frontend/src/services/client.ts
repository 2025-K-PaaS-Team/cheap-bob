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
    baseURL: `${BASE}/seller/store`,
    withCredentials: false,
    headers: { "Content-Type": "application/json" },
  })
);

export const sellerProductApi = attachInterceptors(
  axios.create({
    baseURL: `${BASE}/seller/store/products`,
    withCredentials: false,
    headers: { "Content-Type": "application/json" },
  })
);

export const sellerOrderApi = attachInterceptors(
  axios.create({
    baseURL: `${BASE}/seller/store/orders`,
    withCredentials: false,
    headers: { "Content-Type": "application/json" },
  })
);

export const paymentApi = attachInterceptors(
  axios.create({
    baseURL: `${BASE}/customer/payment`,
    withCredentials: false,
    headers: { "Content-Type": "application/json" },
  })
);

export const customerSearchApi = attachInterceptors(
  axios.create({
    baseURL: `${BASE}/customer/search/stores`,
    withCredentials: false,
    headers: { "Content-Type": "application/json" },
  })
);

export const customerPaymentApi = attachInterceptors(
  axios.create({
    baseURL: `${BASE}/customer/payment`,
    withCredentials: false,
    headers: { "Content-Type": "application/json" },
  })
);

export const customerOrderApi = attachInterceptors(
  axios.create({
    baseURL: `${BASE}/customer/orders`,
    withCredentials: false,
    headers: { "Content-Type": "application/json" },
  })
);

export const customerProfileApi = attachInterceptors(
  axios.create({
    baseURL: `${BASE}/customer/profile`,
    withCredentials: false,
    headers: { "Content-Type": "application/json" },
  })
);

export const optionInfoApi = attachInterceptors(
  axios.create({
    baseURL: `${BASE}/common/options`,
    withCredentials: false,
    headers: { "Content-Type": "application/json" },
  })
);

// kakao
const kakaoAttachInterceptors = (instance: AxiosInstance) => {
  instance.interceptors.request.use((config) => {
    const token = import.meta.env.VITE_KAKAO_REST_API;
    if (token) {
      config.headers = config.headers ?? {};
      config.headers.Authorization = `KakaoAK ${token}`;
    }
    return config;
  });
  return instance;
};

export const kakaoApi = kakaoAttachInterceptors(
  axios.create({
    baseURL: `https://dapi.kakao.com/v2/local/search/address.json`,
    withCredentials: false,
    headers: { "Content-Type": "application/json" },
  })
);
