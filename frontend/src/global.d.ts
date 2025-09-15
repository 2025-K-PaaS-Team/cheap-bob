export {};

declare global {
  interface Window {
    naver: any;
    daum: any;
  }
}

declare module "swiper/css";
declare module "swiper/css/navigation";
declare module "swiper/css/pagination";
