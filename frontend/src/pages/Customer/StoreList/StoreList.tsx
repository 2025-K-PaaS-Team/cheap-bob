import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import {
  AddFavoriteStore,
  GetPreferMenu,
  GetStoreByLocation,
  getStores,
  RemoveFavoriteStore,
} from "@services";
import { Chips, CommonModal } from "@components/common";
import { dongData, NutritionList } from "@constant";
import type { PreferMenuBaseType, StoreSearchType } from "@interface";
import { StoreBox } from "@components/customer/storeList";
import CommonLoading from "@components/common/CommonLoading";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { Loader2 } from "lucide-react";

const StoreList = () => {
  interface Dongs {
    [key: string]: boolean;
  }

  const navigate = useNavigate();

  const scrollRef = useRef<HTMLDivElement | null>(null);
  const sentinelRef = useRef<HTMLDivElement | null>(null);
  const sido = localStorage.getItem("sido") || "서울";
  const sigungu = localStorage.getItem("sigungu") || "관악구";
  const dongsStr = localStorage.getItem("dongs") || "{}";
  const dongs: Dongs = JSON.parse(dongsStr);

  const selectedDongs = useMemo(() => {
    if (dongs["관악구 전체"]) {
      return dongData["관악구"];
    } else {
      return Object.keys(dongs).filter((key) => dongs[key]);
    }
  }, [dongs]);

  const [stores, setStores] = useState<StoreSearchType>();
  const [pageIdx, setPageIdx] = useState<number>(0);

  const [isInitialLoading, setIsInitialLoading] = useState<boolean>(true);
  const [isFetchingMore, setIsFetchingMore] = useState<boolean>(false);

  const [showModal, setShowModal] = useState<boolean>(false);
  const [modalMsg, setModalMsg] = useState("");
  const [selected, setSelected] = useState<Record<string, boolean>>({
    all: true,
  });
  const [isPreferLoaded, setIsPreferLoaded] = useState(false);

  const [loadFailed, setLoadFailed] = useState(false);

  const loadPreferredMenus = async () => {
    try {
      const localSelectedStr = localStorage.getItem("preferredMenus");
      if (localSelectedStr) {
        setSelected(JSON.parse(localSelectedStr));
      } else {
        const res = await GetPreferMenu();
        const selectedFromApi: Record<string, boolean> = { all: false };

        res.preferred_menus.forEach((menu: PreferMenuBaseType) => {
          selectedFromApi[menu.menu_type] = true;
        });

        if (Object.keys(selectedFromApi).length === 1) {
          selectedFromApi.all = true;
        }

        setSelected(selectedFromApi);
        localStorage.setItem("preferredMenus", JSON.stringify(selectedFromApi));
      }
    } catch {
      setSelected({ all: true });
    } finally {
      setIsPreferLoaded(true);
    }
  };

  const filteredStores = useMemo(() => {
    if (!stores) return [];
    const activeKeys = Object.keys(selected).filter(
      (k) => k !== "all" && selected[k]
    );
    const showAll = selected.all || activeKeys.length === 0;
    if (showAll) return stores.stores;

    return stores.stores.filter((store) =>
      store.products.some((p) =>
        p.nutrition_types.some((type) => activeKeys.includes(type))
      )
    );
  }, [stores, selected]);

  const handleGetStores = useCallback(
    async (page: number) => {
      if (page > 0 && stores?.is_end) return;
      if (loadFailed) return;

      try {
        if (page === 0) setIsInitialLoading(true);
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

        setLoadFailed(false);
      } catch {
        setModalMsg("가게 불러오기에 실패했습니다.");
        setShowModal(true);
        setLoadFailed(true);
      } finally {
        if (page === 0) setIsInitialLoading(false);
        else setIsFetchingMore(false);
      }
    },
    [stores, loadFailed, dongs, selectedDongs, sido, sigungu]
  );

  const handleUpdateFavorStore = async (storeId: string, nowFavor: boolean) => {
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
      setModalMsg("선호 가게 업데이트에 실패했습니다.");
      setShowModal(true);
    }
  };

  useEffect(() => {
    loadPreferredMenus();
    handleGetStores(0);
  }, [handleGetStores]);

  useEffect(() => {
    if (isPreferLoaded) {
      localStorage.setItem("preferredMenus", JSON.stringify(selected));
    }
  }, [selected, isPreferLoaded]);

  useEffect(() => {
    if (pageIdx === 0) return;
    handleGetStores(pageIdx);
  }, [pageIdx, handleGetStores]);

  useEffect(() => {
    const sentinel = sentinelRef.current;
    if (!sentinel) return;

    const rootEl = scrollRef.current ?? null;

    const observer = new IntersectionObserver(
      (entries) => {
        const entry = entries[0];
        if (!entry.isIntersecting) return;

        if (!stores?.is_end && !isFetchingMore && !isInitialLoading) {
          setPageIdx((prev) => prev + 1);
        }
      },
      {
        root: rootEl,
        rootMargin: "0px 0px 100px 0px",
        threshold: 0,
      }
    );

    observer.observe(sentinel);
    return () => observer.disconnect();
  }, [stores?.is_end, isFetchingMore, isInitialLoading]);

  if (isInitialLoading && !stores) {
    return <CommonLoading type="data" isLoading={true} />;
  }

  return (
    <div ref={scrollRef} className="flex flex-col px-[20px] app-scroll h-full">
      <div className="border border-1 border-main-deep flex flex-row justify-between px-[18px] py-[16px] h-[54px] rounded-[50px]">
        <input
          type="text"
          onClick={() => navigate("/c/stores/search")}
          className="focus:outline-none"
          placeholder="랜덤팩을 찾으시나요?"
        />
        <img src="/icon/search.svg" alt="searchIcon" />
      </div>

      <Chips
        chips={NutritionList}
        selected={selected}
        setSelected={setSelected}
      />

      <div className="flex flex-col gap-y-[10px] justify-center">
        {filteredStores.length > 0 ? (
          <StoreBox
            stores={filteredStores}
            onToggleFavorite={handleUpdateFavorStore}
          />
        ) : (
          <div className="text-center text-gray-500 py-8">
            조건에 맞는 가게가 없습니다.
          </div>
        )}
      </div>

      <div className="min-h-[100px] flex items-center justify-center">
        {isFetchingMore && (
          <motion.div
            animate={{
              rotate: 360,
              scale: [1, 1.1, 1],
            }}
            transition={{
              rotate: { duration: 1.5, repeat: Infinity, ease: "linear" },
              scale: { duration: 1.5, repeat: Infinity, ease: "easeInOut" },
            }}
          >
            <Loader2 className="w-7 h-7 text-main-deep" />
          </motion.div>
        )}
      </div>

      <div ref={sentinelRef} style={{ height: 1 }} />

      {showModal && (
        <CommonModal
          desc={modalMsg}
          confirmLabel="확인"
          onConfirmClick={() => setShowModal(false)}
          category="green"
        />
      )}
    </div>
  );
};

export default StoreList;
