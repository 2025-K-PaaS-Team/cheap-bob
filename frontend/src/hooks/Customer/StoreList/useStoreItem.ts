import { useMemo } from "react";
import dayjs from "dayjs";
import { getRoundedPrice } from "@utils";
import type { StoreSearchBaseType } from "@interface";
import { buildWindow, inWindow } from "dayjs-time-window";

export const useStoreItem = (store: StoreSearchBaseType) => {
  const now = dayjs();
  const todayDow = (now.day() + 6) % 7;

  const { isOpen, pickupTimeStr, walkingText } = useMemo(() => {
    const todayOp = store.operation_times.find(
      (dow) => dow.day_of_week === todayDow
    );

    const { start: openStart, end: openEnd } = buildWindow(
      todayOp?.open_time,
      todayOp?.close_time
    );

    const isStoreOpenWindow =
      !!todayOp?.is_open_enabled && inWindow(now, openStart, openEnd);

    const pStart = todayOp?.pickup_start_time?.slice(0, 5) || "00:00";
    const pEnd = todayOp?.pickup_end_time?.slice(0, 5) || "00:00";

    let walkTxt = null;
    if (store.address.nearest_station && store.address.walking_time > 0) {
      walkTxt = `${store.address.nearest_station} 도보 ${store.address.walking_time}분`;
    }

    return {
      isOpen: isStoreOpenWindow,
      pickupTimeStr: `${pStart} ~ ${pEnd}`,
      walkingText: walkTxt,
    };
  }, [store, todayDow, now]);

  const product = store.products?.[0];

  const productInfo = useMemo(() => {
    if (!product) return null;

    const isSoldOut = product.current_stock < 1;
    const finalPrice = getRoundedPrice(product.price, product.sale);

    return {
      stock: product.current_stock,
      price: product.price,
      finalPrice,
      isSoldOut,
    };
  }, [product]);

  const mainImage = store.images.find((img) => img.is_main)?.image_url;

  return {
    isOpen,
    pickupTimeStr,
    walkingText,
    productInfo,
    mainImage,
  };
};
