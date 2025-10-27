import axios, { type AxiosInstance } from "axios";

const BASE = `${import.meta.env.VITE_API_BASE_URL}/api/v1`;

const attachInterceptors = (instance: AxiosInstance) => {
  instance.interceptors.response.use(
    (response) => response,
    (error) => {
      const status = error.response?.status;
      const isHome =
        window.location.pathname === "/c" ||
        window.location.pathname === "/s" ||
        window.location.pathname === "/";

      const isWithdraw = window.location.pathname.startsWith("/withdraw");

      // 401 Unauthorize
      if (status === 401 && !isHome && !isWithdraw) {
        window.location.href = "/auth/role-check";
      }

      // 439 Withdrawn user
      if (status === 439) {
        window.location.href = "/withdraw/cancel";
      }

      return Promise.reject(error);
    }
  );

  return instance;
};

export const api = attachInterceptors(
  axios.create({
    baseURL: BASE,
    withCredentials: true,
    headers: { "Content-Type": "application/json" },
  })
);

export const authApi = attachInterceptors(
  axios.create({
    baseURL: `${BASE}/auth`,
    withCredentials: true,
    headers: { "Content-Type": "application/json" },
  })
);

export const userApi = attachInterceptors(
  axios.create({
    baseURL: `${BASE}/user/role`,
    withCredentials: true,
    headers: { "Content-Type": "application/json" },
  })
);

export const sellerStoreApi = attachInterceptors(
  axios.create({
    baseURL: `${BASE}/seller/store`,
    withCredentials: true,
    headers: { "Content-Type": "application/json" },
  })
);

export const sellerStoreProfileApi = attachInterceptors(
  axios.create({
    baseURL: `${BASE}/seller/store/profile`,
    withCredentials: true,
    headers: { "Content-Type": "application/json" },
  })
);

export const sellerStoreSnsApi = attachInterceptors(
  axios.create({
    baseURL: `${BASE}/seller/store/sns`,
    withCredentials: true,
    headers: { "Content-Type": "application/json" },
  })
);

export const sellerStoreSettingsApi = attachInterceptors(
  axios.create({
    baseURL: `${BASE}/seller/store/settings`,
    withCredentials: true,
    headers: { "Content-Type": "application/json" },
  })
);

export const sellerStoreImgApi = attachInterceptors(
  axios.create({
    baseURL: `${BASE}/seller/store/images`,
    withCredentials: true,
    headers: { "Content-Type": "application/json" },
  })
);

export const sellerProductApi = attachInterceptors(
  axios.create({
    baseURL: `${BASE}/seller/store/products`,
    withCredentials: true,
    headers: { "Content-Type": "application/json" },
  })
);

export const sellerOrderApi = attachInterceptors(
  axios.create({
    baseURL: `${BASE}/seller/store/orders`,
    withCredentials: true,
    headers: { "Content-Type": "application/json" },
  })
);

export const sellerSettlementApi = attachInterceptors(
  axios.create({
    baseURL: `${BASE}/seller/store/settlement`,
    withCredentials: true,
    headers: { "Content-Type": "application/json" },
  })
);

export const sellerWithdrawApi = attachInterceptors(
  axios.create({
    baseURL: `${BASE}/seller/withdraw`,
    withCredentials: true,
    headers: { "Content-Type": "application/json" },
  })
);

export const paymentApi = attachInterceptors(
  axios.create({
    baseURL: `${BASE}/customer/payment`,
    withCredentials: true,
    headers: { "Content-Type": "application/json" },
  })
);

export const customerSearchApi = attachInterceptors(
  axios.create({
    baseURL: `${BASE}/customer/search/stores`,
    withCredentials: true,
    headers: { "Content-Type": "application/json" },
  })
);

export const customerSearchHistoryApi = attachInterceptors(
  axios.create({
    baseURL: `${BASE}/customer/history/search`,
    withCredentials: true,
    headers: { "Content-Type": "application/json" },
  })
);

export const customerPaymentApi = attachInterceptors(
  axios.create({
    baseURL: `${BASE}/customer/payment`,
    withCredentials: true,
    headers: { "Content-Type": "application/json" },
  })
);

export const customerWithdrawApi = attachInterceptors(
  axios.create({
    baseURL: `${BASE}/customer/withdraw`,
    withCredentials: true,
    headers: { "Content-Type": "application/json" },
  })
);

export const customerOrderApi = attachInterceptors(
  axios.create({
    baseURL: `${BASE}/customer/orders`,
    withCredentials: true,
    headers: { "Content-Type": "application/json" },
  })
);

export const customerRegisterApi = attachInterceptors(
  axios.create({
    baseURL: `${BASE}/customer/register`,
    withCredentials: true,
    headers: { "Content-Type": "application/json" },
  })
);

export const customerProfileApi = attachInterceptors(
  axios.create({
    baseURL: `${BASE}/customer/profile`,
    withCredentials: true,
    headers: { "Content-Type": "application/json" },
  })
);

export const optionInfoApi = attachInterceptors(
  axios.create({
    baseURL: `${BASE}/common/options`,
    withCredentials: true,
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
