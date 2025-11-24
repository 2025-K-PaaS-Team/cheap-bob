import { useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { Chips, CommonModal, CommonLoading } from "@components/common";
import {
  LoadingSpinner,
  SearchBar,
  StoreBox,
} from "@components/customer/storeList";
import { NutritionList } from "@constant";

import {
  useInfiniteScroll,
  useStoreFilter,
  useStoreList,
  useStoreLocation,
} from "@hooks/Customer/StoreList";

const StoreList = () => {
  const navigate = useNavigate();

  const { sido, sigungu, dongs, selectedDongs } = useStoreLocation();

  const {
    stores,
    isLoading,
    isFetchingMore,
    isEnd,
    error,
    fetchStores,
    toggleFavorite,
    clearError,
  } = useStoreList(sido, sigungu, dongs, selectedDongs);

  const { selected, setSelected, filteredStores } = useStoreFilter(stores);

  const [pageIdx, setPageIdx] = useState(0);

  useEffect(() => {
    fetchStores(pageIdx);
  }, [pageIdx, fetchStores]);

  const loadMore = useCallback(() => setPageIdx((prev) => prev + 1), []);
  const shouldLoad = !isLoading && !isFetchingMore && !isEnd;

  const sentinelRef = useInfiniteScroll(loadMore, shouldLoad);

  if (isLoading && !stores)
    return <CommonLoading type="data" isLoading={true} />;

  return (
    <div className="flex flex-col px-[20px] app-scroll h-full">
      <SearchBar onClick={() => navigate("/c/stores/search")} />

      <Chips
        chips={NutritionList}
        selected={selected}
        setSelected={setSelected}
      />

      <div className="flex flex-col gap-y-[10px] justify-center">
        {filteredStores.length > 0 ? (
          <StoreBox stores={filteredStores} onToggleFavorite={toggleFavorite} />
        ) : (
          <div className="text-center text-gray-500 py-8">
            조건에 맞는 가게가 없습니다.
          </div>
        )}
      </div>

      <div className="min-h-[100px] flex items-center justify-center">
        {isFetchingMore && <LoadingSpinner />}
      </div>

      <div ref={sentinelRef} style={{ height: 1 }} />

      {error && (
        <CommonModal
          desc={error}
          confirmLabel="확인"
          onConfirmClick={clearError}
          category="green"
        />
      )}
    </div>
  );
};

export default StoreList;
