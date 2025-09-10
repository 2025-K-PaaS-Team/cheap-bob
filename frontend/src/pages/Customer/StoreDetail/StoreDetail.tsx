import PortOneLab from "@components/Lab/PortoneLab";
import type { StoreDetailType } from "@interface";
import { getSpecificStore } from "@services";
import { useEffect, useState } from "react";
import { useParams } from "react-router";

const StoreDetail = () => {
  const { storeId } = useParams<{ storeId: string }>();
  const [store, setStore] = useState<StoreDetailType | null>(null);

  const hadnleGetSpecificStore = async (id: string) => {
    try {
      const store = await getSpecificStore(id);
      setStore(store);
    } catch (err: unknown) {
      console.error("등록 실패:", err);
      const msg = err instanceof Error ? err.message : "실패했슈...";
      console.log(msg);
    }
  };

  useEffect(() => {
    if (storeId) {
      hadnleGetSpecificStore(storeId);
    }
  }, [storeId]);

  return (
    <div className="">
      {store && (
        <div className="flex flex-col gap-y-5 justify-center p-8">
          <h3>가게 이름: {store.store_name}</h3>
          <div key={store.store_name} className="gap-y-5 flex flex-col">
            {store.products.map((p, idx) => (
              <div
                key={idx}
                className="border-1 border-gray-400 shadow-md rounded-lg flex flex-col gap-y-2"
              >
                <img
                  src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRyMNzjqxn4hQQ8bmPj7I1VN8DEWEKf5AsILQ&s"
                  className="flex items-center justify-center w-full"
                  alt="dummyProductImg"
                />
                <div key={p.product_id} className="font-bold">
                  {p.product_name}
                  {p.price}원 (재고 {p.stock})
                </div>
                {storeId && <PortOneLab storeId={storeId} product={p} />}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default StoreDetail;
