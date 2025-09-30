import { useNavigate } from "react-router";
import { useEffect, useState } from "react";
import type { StoreResponseType } from "@interface";
import { getStores } from "@services";
import { Chips } from "@components/common";
import { NutritionList } from "@constant";

const StoreList = () => {
  const [stores, setStores] = useState<StoreResponseType[] | null>([]);
  const navigate = useNavigate();
  const [selected, setSelected] = useState<Record<string, boolean>>(
    NutritionList.reduce((acc, item) => {
      acc[item.key] = false;
      return acc;
    }, {} as Record<string, boolean>)
  );

  // get stores list
  const handleGetStores = async () => {
    try {
      const stores = await getStores();
      console.log("get stores 성공", stores);
      setStores(stores);
    } catch (err: unknown) {
      console.error("get stores fail");
    }
  };

  useEffect(() => {
    handleGetStores();
  }, []);

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

      <div className="flex flex-col gap-y-5 justify-center p-8">
        {stores ? (
          stores.map((store) => (
            <div
              className="flex flex-col h-[212px]"
              onClick={() => handleClickStore({ store_id: store.store_id })}
              key={store.store_id}
            >
              <div className="h-[125px] overflow-hidden">
                <img
                  src="https://img1.daumcdn.net/thumb/R1280x0/?scode=mtistory2&fname=https%3A%2F%2Fblog.kakaocdn.net%2Fdna%2FbqXxZF%2FbtsNKfB5NZ6%2FAAAAAAAAAAAAAAAAAAAAANSGr0mk3BaSXPwBe-A08VCC2nbuIh9kfKJUmoQYzcZ9%2Ftfile.jpg%3Fcredential%3DyqXZFxpELC7KVnFOS48ylbz2pIh7yKj8%26expires%3D1759244399%26allow_ip%3D%26allow_referer%3D%26signature%3DnxT61ICyKtLw3d%252BEs6purwNlAOY%253D"
                  alt="locationIcon"
                  className="w-full"
                />
              </div>
              <div className="bg-[#8088C0] p-[15px] flex flex-1 flex-col gap-y-[7px]">
                <div className="flex flex-row justify-between h-full items-end">
                  <div className="text-[15px] font-bold">가게 이름</div>

                  <div className="bg-[#BFBFBF] p-[5px] rounded-[10px] text-[10px]">
                    원가
                  </div>
                </div>

                <div className="flex flex-row justify-between h-full">
                  <div className="flex flex-row gap-x-[12px] items-center">
                    <div className="text-[12px]">픽업 시간</div>
                    <div className="bg-[#BFBFBF] p-[5px] rounded-[10px] text-[12px]">
                      XX:XX ~ ZZ:ZZ
                    </div>
                  </div>
                  <div className="bg-[#BFBFBF] p-[5px] rounded-[10px] text-[11px]">
                    판매금액
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
