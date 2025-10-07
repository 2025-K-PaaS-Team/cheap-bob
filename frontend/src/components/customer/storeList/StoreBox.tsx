import dayjs from "dayjs";
import { useNavigate } from "react-router";
import type { StoreSearchBaseType } from "@interface";

interface StoreBoxProps {
  stores: StoreSearchBaseType[];
  onToggleFavorite?: (storeId: string, nowFavor: boolean) => void;
}

const StoreBox = ({ stores, onToggleFavorite }: StoreBoxProps) => {
  const navigate = useNavigate();
  const todayDow = dayjs().day();

  const handleClickStore = (store_id: string) => {
    navigate(`${store_id}`);
  };

  return (
    <>
      {stores.map((store) => (
        <div
          key={store.store_id}
          className="flex flex-col h-[212px] relative"
          onClick={() => handleClickStore(store.store_id)}
        >
          {/* favor */}
          <div
            className={`rounded-full absolute top-1 right-1 z-10 w-[41px] h-[41px] p-[5px] ${
              store.is_favorite ? "bg-red-300" : "bg-[#d9d9d9]"
            } flex justify-center items-center`}
            onClick={(e) => {
              e.stopPropagation();
              onToggleFavorite?.(store.store_id, store.is_favorite);
            }}
          >
            <img
              src="/icon/heart.svg"
              alt="FavoriteStore"
              className="w-5 h-5"
            />
          </div>

          {/* now open */}
          <div className="bg-[#d9d9d9] rounded-[10px] absolute top-1 left-1 z-10 p-[5px]">
            {store.operation_times.find((dow) => dow.day_of_week === todayDow)
              ?.is_currently_open
              ? "영업중"
              : "영업 종료"}
          </div>

          {/* store image */}
          <div className="h-[125px] overflow-hidden relative">
            <img
              src={store.images.find((img) => img.is_main)?.image_url}
              alt="StoreImage"
              className="w-full object-none"
            />
          </div>

          {/* store info*/}
          <div className="bg-[#8088C0] p-[15px] flex flex-1 flex-col gap-y-[7px]">
            <div className="flex flex-row justify-between h-full items-end">
              <div className="text-[15px] font-bold">{store.store_name}</div>
              <div className="bg-[#BFBFBF] p-[5px] rounded-[10px] text-[10px]">
                {store.products[0].price} 원
              </div>
            </div>

            <div className="flex flex-row justify-between h-full">
              <div className="flex flex-row gap-x-[12px] items-center">
                <div className="text-[12px]">픽업 시간</div>
                <div className="bg-[#BFBFBF] p-[5px] rounded-[10px] text-[12px]">
                  {store.operation_times
                    .find((dow) => dow.day_of_week === todayDow)
                    ?.pickup_start_time.slice(0, 5)}
                  ~
                  {store.operation_times
                    .find((dow) => dow.day_of_week === todayDow)
                    ?.pickup_end_time.slice(0, 5)}
                </div>
              </div>
              <div className="bg-[#BFBFBF] p-[5px] rounded-[10px] text-[11px]">
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
