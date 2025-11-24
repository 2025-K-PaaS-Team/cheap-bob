import { memo } from "react";
import type { StoreSearchBaseType } from "@interface";
import { useStoreItem } from "@hooks/Customer/StoreList";

interface StoreCardProps {
  store: StoreSearchBaseType;
  onClick: (store: StoreSearchBaseType) => void;
  onToggleFavorite?: (storeId: string, nowFavor: boolean) => void;
}

export const StoreCard = memo(
  ({ store, onClick, onToggleFavorite }: StoreCardProps) => {
    const { isOpen, pickupTimeStr, walkingText, productInfo, mainImage } =
      useStoreItem(store);

    const handleFavoriteClick = (e: React.MouseEvent) => {
      e.stopPropagation();
      onToggleFavorite?.(store.store_id, store.is_favorite);
    };

    return (
      <div
        className="flex flex-col h-[235px] relative cursor-pointer"
        onClick={() => onClick(store)}
      >
        {/* --- 좋아요 버튼 --- */}
        <div
          className="rounded-full absolute top-1 right-1 z-10 w-[41px] h-[41px] p-[5px] flex justify-center items-center"
          onClick={handleFavoriteClick}
        >
          <img
            src={store.is_favorite ? "/icon/heartFull.svg" : "/icon/heart.svg"}
            alt="Favorite"
            width="24px"
          />
        </div>

        {/* --- 가게 이미지 영역 --- */}
        <div className="h-[131px] rounded-t overflow-hidden relative">
          {/* 영업 상태 태그 */}
          <div className="tagFont bg-custom-white rounded-lg absolute bottom-2 left-2 z-10 py-[4px] px-[10px]">
            {isOpen ? "영업중" : "영업 종료"}
          </div>

          {/* 도보 시간 태그 */}
          {walkingText && (
            <div className="tagFont bg-custom-black text-custom-white rounded-sm absolute bottom-2 right-2 z-10 py-[4px] px-[10px]">
              {walkingText}
            </div>
          )}

          {/* 이미지 */}
          <img
            src={mainImage}
            alt={store.store_name}
            className="w-full h-full object-center object-cover"
          />
        </div>

        {/* --- 정보 영역 --- */}
        <div className="bg-white rounded-b shadow p-[15px] flex flex-1 flex-col gap-y-[7px] relative">
          {/* 1. 가게 이름 */}
          <div className="text-[15px] font-bold truncate">
            {store.store_name}
          </div>

          {/* 2. 픽업 시간 */}
          <div className="flex flex-row gap-x-[12px] items-center font-bold tagFont">
            <span>픽업 시간</span>
            <span>{pickupTimeStr}</span>
          </div>

          {/* 3. 재고 상태 (ProductInfo가 있을 때만 렌더링) */}
          {productInfo && (
            <div className="flex flex-row justify-between tagFont mt-auto">
              <div className="bg-[#E7E7E7] rounded-sm py-[5.5px] px-[10px]">
                패키지{" "}
                {productInfo.isSoldOut ? (
                  <span className="text-sub-orange font-bold">품절</span>
                ) : (
                  <span className="text-main-deep font-bold">
                    {productInfo.stock}개 남음
                  </span>
                )}
              </div>
            </div>
          )}

          {/* 4. 가격 (우측 하단 절대 위치) */}
          {productInfo && (
            <div className="absolute right-[15px] bottom-[15px] text-end">
              <div className="tagFont text-[#9D9D9D] line-through">
                {productInfo.price.toLocaleString()}
              </div>
              <h1
                className={`font-bold ${
                  productInfo.isSoldOut ? "text-[#9d9d9d]" : "text-sub-orange"
                }`}
              >
                {productInfo.finalPrice.toLocaleString()}원
              </h1>
            </div>
          )}
        </div>
      </div>
    );
  }
);

StoreCard.displayName = "StoreCard";
