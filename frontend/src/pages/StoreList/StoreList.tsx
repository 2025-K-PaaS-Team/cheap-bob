import { useNavigate } from "react-router";
import { useEffect, useState } from "react";
import type { StoreResponseType } from "@interface";
import { getStores } from "@services";

const StoreList = () => {
  const [stores, setStores] = useState<StoreResponseType[] | null>([]);
  const navigate = useNavigate();

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
    <div className="flex flex-col gap-y-5 justify-center p-8">
      {stores ? (
        stores.map((store) => (
          // store
          <div
            className="border-1 border-gray-400 shadow-md rounded-lg flex flex-col"
            onClick={() => handleClickStore({ store_id: store.store_id })}
            key={store.store_id}
          >
            {/* img */}
            <img
              src={
                "https://mediahub.seoul.go.kr/uploads/mediahub/2024/01/ZmynWCLNyAQNfWWDfmSaLEByeOPGsaWZ.jpg"
              }
              alt="dummyStoreImg"
            />
            {/* desc */}
            <div className="flex flex-row justify-between items-center p-4">
              {/* store info left */}
              <div>
                <div className="font-bold">{store.store_name}</div>
              </div>
            </div>
          </div>
        ))
      ) : (
        <div>loading</div>
      )}
    </div>
  );
  0;
};

export default StoreList;
