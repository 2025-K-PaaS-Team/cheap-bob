import { useState, useCallback, useRef } from "react";
import {
  GetStoreByLocation,
  getStores,
  AddFavoriteStore,
  RemoveFavoriteStore,
} from "@services";
import type { StoreSearchType } from "@interface";

interface Dongs {
  [key: string]: boolean;
}

export const useStoreList = (
  sido: string,
  sigungu: string,
  dongs: Dongs,
  selectedDongs: string[]
) => {
  const [stores, setStores] = useState<StoreSearchType>();
  const [isLoading, setIsLoading] = useState(false); // 초기 로딩
  const [isFetchingMore, setIsFetchingMore] = useState(false); // 추가 로딩
  const [error, setError] = useState<string | null>(null);

  // 핵심: stores 상태 변경으로 인한 useEffect 루프를 막기 위해 Ref 사용
  const isEndRef = useRef(false);

  const fetchStores = useCallback(
    async (page: number) => {
      // 이미 끝났거나 로딩 중이면 중단 (page가 0일 때는 초기화이므로 진행)
      if (page > 0 && isEndRef.current) return;

      try {
        if (page === 0) setIsLoading(true);
        else setIsFetchingMore(true);

        let newStores;

        if (dongs && selectedDongs.length > 0) {
          newStores = await GetStoreByLocation(
            sido,
            sigungu,
            selectedDongs,
            page
          );
        } else {
          newStores = await getStores(page);
        }

        setStores((prev) => {
          if (!prev || page === 0) return newStores;
          return {
            stores: [...prev.stores, ...newStores.stores],
            is_end: newStores.is_end,
          };
        });

        // Ref 업데이트 (렌더링 유발 X)
        isEndRef.current = newStores.is_end;
        setError(null);
      } catch {
        setError("가게 불러오기에 실패했습니다.");
      } finally {
        setIsLoading(false);
        setIsFetchingMore(false);
      }
    },
    [sido, sigungu, dongs, selectedDongs]
  );

  const toggleFavorite = async (storeId: string, nowFavor: boolean) => {
    try {
      if (!nowFavor) await AddFavoriteStore(storeId);
      else await RemoveFavoriteStore(storeId);

      setStores((prev) =>
        prev
          ? {
              ...prev,
              stores: prev.stores.map((s) =>
                s.store_id === storeId ? { ...s, is_favorite: !nowFavor } : s
              ),
            }
          : prev
      );
    } catch {
      setError("선호 가게 업데이트에 실패했습니다.");
    }
  };

  const clearError = () => setError(null);

  return {
    stores,
    isLoading,
    isFetchingMore,
    error,
    isEnd: isEndRef.current,
    fetchStores,
    toggleFavorite,
    clearError,
  };
};
