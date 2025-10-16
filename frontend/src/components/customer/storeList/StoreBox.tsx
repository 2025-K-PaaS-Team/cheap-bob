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
    navigate(`${store.store_id}`, { state: { store } });
  };

  return (
    <>
      {stores.map((store) => (
        <div
          key={store.store_id}
          className="flex flex-col h-[212px] relative"
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
              <img
                src="/icon/heartFull.svg"
                alt="FavoriteStore"
                className="w-5 h-5"
              />
            ) : (
              <img
                src="/icon/heart.svg"
                alt="FavoriteStore"
                className="w-5 h-5"
              />
            )}
          </div>

          {/* store image */}
          <div className="h-[125px] rounded-t overflow-hidden relative">
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
            <div className="flex flex-row justify-between h-full items-end">
              <div className="text-[15px] font-bold">{store.store_name}</div>
              <div className="bg-[#BFBFBF] p-[5px] rounded text-[10px]">
                {store.products[0].price} 원
              </div>
            </div>

            <div className="flex flex-row justify-between h-full">
              <div className="flex flex-row gap-x-[12px] items-center">
                <div className="text-[12px]">픽업 시간</div>
                <div className="bg-[#BFBFBF] p-[5px] rounded text-[12px]">
                  {store.operation_times
                    .find((dow) => dow.day_of_week === todayDow)
                    ?.pickup_start_time.slice(0, 5)}
                  ~
                  {store.operation_times
                    .find((dow) => dow.day_of_week === todayDow)
                    ?.pickup_end_time.slice(0, 5)}
                </div>
              </div>
              <div className="bg-[#BFBFBF] p-[5px] rounded text-[11px]">
                {(store.products[0].price * store.products[0].sale) / 100}원
              </div>
            </div>
          </div>
        </div>
      ))}
    </>
  );
};

export default StoreBox;
