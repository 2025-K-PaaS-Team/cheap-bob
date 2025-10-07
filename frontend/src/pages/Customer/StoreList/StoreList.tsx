import { useNavigate } from "react-router";
import { useEffect, useState } from "react";
import { getStores } from "@services";
import { Chips } from "@components/common";
import { NutritionList } from "@constant";
import type { StoreSearchType } from "@interface";
import dayjs from "dayjs";

const StoreList = () => {
  const [stores, setStores] = useState<StoreSearchType>();
  const [pageIdx, setPageIdx] = useState<number>(0);
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(false);
  const [selected, setSelected] = useState<Record<string, boolean>>(
    NutritionList.reduce((acc, item) => {
      acc[item.key] = false;
      return acc;
    }, {} as Record<string, boolean>)
  );
  const todayDow = dayjs().day();
  const filteredStores = stores?.stores.filter((store) => {
    const activeKeys = Object.keys(selected).filter((key) => selected[key]);
    if (activeKeys.length === 0) return true;

    return store.products.some((p) =>
      p.nutrition_types.some((type) => activeKeys.includes(type))
    );
  });

  // get stores list
  const handleGetStores = async (pageIdx: number) => {
    if (isLoading) return;
    if (stores?.is_end) return;

    try {
      setIsLoading(true);
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
      console.error("get stores fail");
    } finally {
      setIsLoading(false);
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

  // go to specific store detail page
  const handleClickStore = ({ store_id }: { store_id: string }) => {
    if (!store_id) return;
    navigate(`${store_id}`);
  };

  return (
    <div className="flex flex-col px-[20px]">
      <Chips
        chips={NutritionList}
        selected={selected}
        setSelected={setSelected}
      />

      <div className="flex flex-col gap-y-[10px] justify-center">
        {filteredStores ? (
          filteredStores.map((store) => (
            <div
              className="flex flex-col h-[212px] relative"
              onClick={() => handleClickStore({ store_id: store.store_id })}
              key={store.store_id}
            >
              <div
                className={`rounded-full absolute top-1 right-1 z-10 w-[41px] h-[41px] p-[5px] ${
                  store.is_favorite ? "bg-red-300" : "bg-[#d9d9d9]"
                } flex justify-center items-center`}
              >
                <img
                  src="/icon/heart.svg"
                  alt="FavoriteStore"
                  className="w-5 h-5"
                />
              </div>
              <div className="bg-[#d9d9d9] rounded-[10px] absolute top-1 left-1 z-10 p-[5px]">
                {store.operation_times.find(
                  (dow) => dow.day_of_week === todayDow
                )?.is_currently_open
                  ? "영업중"
                  : "영업 종료"}
              </div>
              <div className="h-[125px] overflow-hidden relative">
                <img
                  src={store.images.find((img) => img.is_main)?.image_url}
                  alt="StoreImage"
                  className="w-ful object-none"
                />
              </div>
              <div className="bg-[#8088C0] p-[15px] flex flex-1 flex-col gap-y-[7px]">
                <div className="flex flex-row justify-between h-full items-end">
                  <div className="text-[15px] font-bold">
                    {store.store_name}
                  </div>

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
          ))
        ) : (
          <div>loading</div>
        )}
      </div>
    </div>
  );
  0;
};

export default StoreList;
