import dayjs from "dayjs";
import { useNavigate } from "react-router";
import type { StoreSearchBaseType } from "@interface";

interface StoreBoxProps {
  stores: StoreSearchBaseType[];
  onToggleFavorite?: (storeId: string, nowFavor: boolean) => void;
}

const StoreBox = ({ stores, onToggleFavorite }: StoreBoxProps) => {
  const navigate = useNavigate();
  const todayDow = (dayjs().day() + 6) % 7;

  const handleClickStore = (store: StoreSearchBaseType) => {
    navigate(`/c/stores/${store.store_id}`, { state: { store } });
  };

  return (
    <>
      {stores.map((store) => (
        <div
          key={store.store_id}
          className="flex flex-col h-[235px] relative"
          onClick={() => handleClickStore(store)}
        >
          {/* favor */}
          <div
            className="rounded-full absolute top-1 right-1 z-10 w-[41px] h-[41px] p-[5px] flex justify-center items-center"
            onClick={(e) => {
              e.stopPropagation();
              onToggleFavorite?.(store.store_id, store.is_favorite);
            }}
          >
            {store.is_favorite ? (
              <img src="/icon/heartFull.svg" alt="FavoriteStore" width="24px" />
            ) : (
              <img src="/icon/heart.svg" alt="FavoriteStore" width="24px" />
            )}
          </div>

          {/* store image */}
          <div className="h-[131px] rounded-t overflow-hidden relative">
            {/* now open */}
            <div className="bg-custom-white rounded-lg absolute bottom-2 left-2 z-10 py-[4px] px-[10px]">
              {store.operation_times.find((dow) => dow.day_of_week === todayDow)
                ?.is_currently_open
                ? "영업중"
                : "영업 종료"}
            </div>
            <img
              src={store.images.find((img) => img.is_main)?.image_url}
              alt="StoreImage"
              className="w-full object-none"
            />
          </div>

          {/* store info*/}
          <div className="bg-white rounded-b shadow p-[15px] flex flex-1 flex-col gap-y-[7px]">
            {/* first row - store name */}
            <div className="flex flex-row justify-between h-full items-end">
              <div className="text-[15px] font-bold">{store.store_name}</div>
            </div>

            {/* second row - pickup time */}
            <div className="flex flex-row justify-between h-full">
              <div className="flex flex-row gap-x-[12px] items-center font-bold tagFont">
                <div className="">픽업 시간</div>
                <div className="">
                  {store.operation_times
                    .find((dow) => dow.day_of_week === todayDow)
                    ?.pickup_start_time.slice(0, 5)}
                  ~
                  {store.operation_times
                    .find((dow) => dow.day_of_week === todayDow)
                    ?.pickup_end_time.slice(0, 5)}
                </div>
              </div>
            </div>

            {/* third row - pkg remian qty */}
            <div className="flex flex-row justify-between tagFont">
              {/* remain qty */}
              {store.products[0].current_stock == 0 ? (
                <div className="bg-[#E7E7E7] rounded-sm py-[5.5px] px-[10px]">
                  패키지 <span className="text-sub-orange font-bold">품절</span>
                </div>
              ) : (
                <div className="bg-[#E7E7E7] rounded-sm py-[5.5px] px-[10px]">
                  패키지{" "}
                  <span className="text-main-deep font-bold">
                    {store.products[0].current_stock}개 남음
                  </span>
                </div>
              )}
            </div>

            {/* absolute position - price */}
            <div className="absolute right-3 bottom-3 text-end">
              <div className="tagFont text-[#9D9D9D] line-through">
                {store.products[0].price}
              </div>
              <h1
                className={`${
                  store.products[0].current_stock == 0
                    ? "text-[#9d9d9d]"
                    : "text-sub-orange"
                }`}
              >
                {(store.products[0].price * store.products[0].sale) / 100}원
              </h1>
            </div>
          </div>
        </div>
      ))}
    </>
  );
};

export default StoreBox;
