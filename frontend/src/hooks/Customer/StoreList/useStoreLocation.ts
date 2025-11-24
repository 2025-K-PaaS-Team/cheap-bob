import { useMemo } from "react";
import { dongData } from "@constant";

export const useStoreLocation = () => {
  const sido = localStorage.getItem("sido") || "서울";
  const sigungu = localStorage.getItem("sigungu") || "관악구";

  const dongs = useMemo(() => {
    try {
      return JSON.parse(localStorage.getItem("dongs") || "{}");
    } catch {
      return {};
    }
  }, []);

  const selectedDongs = useMemo(() => {
    if (dongs[`${sigungu} 전체`] || dongs["관악구 전체"]) {
      return dongData[sigungu] || dongData["관악구"] || [];
    } else {
      return Object.keys(dongs).filter((key) => dongs[key]);
    }
  }, [dongs, sigungu]);

  return {
    sido,
    sigungu,
    dongs,
    selectedDongs,
  };
};
