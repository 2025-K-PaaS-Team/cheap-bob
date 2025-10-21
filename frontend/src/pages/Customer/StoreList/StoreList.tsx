import { useEffect, useMemo, useState } from "react";
import { AddFavoriteStore, getStores, RemoveFavoriteStore } from "@services";
import { Chips, CommonModal } from "@components/common";
import { NutritionList } from "@constant";
import type { StoreSearchType } from "@interface";
import { StoreBox } from "@components/customer/storeList";
import CommonLoading from "@components/common/CommonLoading";
import { useNavigate } from "react-router";

const StoreList = () => {
  const navigate = useNavigate();
  const [stores, setStores] = useState<StoreSearchType>();
  const [pageIdx, setPageIdx] = useState<number>(0);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  const [showModal, setShowModal] = useState<boolean>(false);
  const [modalMsg, setModalMsg] = useState("");
  const [selected, setSelected] = useState<Record<string, boolean>>({
    all: true,
  });

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

  // get stores list
  const handleGetStores = async (pageIdx: number) => {
    if (stores?.is_end) return;

    try {
      const newStores = await getStores(pageIdx);
      setStores((prev) => {
        if (pageIdx === 0) {
          return newStores;
        } else {
          return {
            stores: prev?.stores
              ? [...prev.stores, ...newStores.stores]
              : newStores.stores,
            is_end: newStores.is_end,
          };
        }
      });
    } catch (err: unknown) {
      setModalMsg("가게 불러오기에 실패했습니다.");
      setShowModal(true);
    } finally {
      setIsLoading(false);
    }
  };

  // add or delete favorite store
  const handleUpdateFavorStore = async (storeId: string, nowFavor: boolean) => {
    try {
      if (!nowFavor) {
        // add favor store
        await AddFavoriteStore(storeId);
      } else {
        // remove favor store
        await RemoveFavoriteStore(storeId);
      }

      await getStores(pageIdx);
      setStores((prev) => ({
        ...prev!,
        stores: prev!.stores.map((s) =>
          s.store_id === storeId ? { ...s, is_favorite: !nowFavor } : s
        ),
      }));
    } catch (err) {
      setModalMsg("선호 가게 업데이트에 실패했습니다.");
      setShowModal(true);
    }
  };

  useEffect(() => {
    handleGetStores(pageIdx);
  }, []);

  useEffect(() => {
    const handleScroll = () => {
      const scrollToTop = window.scrollY;
      const windowHeight = window.innerHeight;
      const docHegiht = document.body.scrollHeight;

      if (scrollToTop + windowHeight >= docHegiht - 100) {
        if (!stores?.is_end) {
          setPageIdx((prev) => prev + 1);
        }
      }
    };

    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  });

  useEffect(() => {
    if (pageIdx === 0) return;
    handleGetStores(pageIdx);
  }, [pageIdx]);

  if (isLoading) {
    return <CommonLoading type="data" isLoading={isLoading} />;
  }

  return (
    <div className="flex flex-col px-[20px]">
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

      <div className="flex flex-col gap-y-[10px] justify-center mb-[30px]">
        {filteredStores ? (
          <StoreBox
            stores={filteredStores}
            onToggleFavorite={handleUpdateFavorStore}
          />
        ) : (
          <div>loading</div>
        )}
      </div>
      {/* show modal */}
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
