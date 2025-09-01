// import { Outlet } from "react-router";
// import { useNavigate } from "react-router";

import { getSpecificStore, getStores } from "@services";
import { useState } from "react";

const CustomerLab = () => {
  // const navigate = useNavigate();
  const [errMsg, setErrMsg] = useState<string | null>(null);
  const [stores, setStores] = useState(null);
  const [store, setStore] = useState(null);

  const handleGetStores = async () => {
    try {
      const stores = await getStores();
      console.log("get stores 성공", stores);
      setStores(stores);
    } catch (err: unknown) {
      console.error("get stores fail");
      const msg = err instanceof Error ? err.message : "실패해소";
      setErrMsg(msg);
    }
  };

  const hadnleGetSpecificStore = async () => {
    try {
      const store = await getSpecificStore("STR_1756711885_298d70b4");
      setStore(store);
    } catch (err: unknown) {
      console.error("등록 실패:", err);
      const msg = err instanceof Error ? err.message : "실패했슈...";
      setErrMsg(msg);
    }
  };

  return (
    <div className="min-h-screen m-5 gap-y-2 flex flex-col justify-center items-center">
      {/* <button
        className={`bg-green-400 p-3 rounded-xl text-center cursor-pointer`}
        onClick={() => navigate("map")}
      >
        NAVER MAP API
      </button> */}
      {/* <Outlet /> */}

      {/* 가게 목록 가져오기 테스트 */}
      <div className="flex flex-col space-y-2 p-2 w-full p-2">
        <h2>가게 목록 가져오기 테스트</h2>
        {/* create product */}
        <button
          className={`bg-green-100 p-3 rounded-xl text-center cursor-pointer`}
          onClick={() => handleGetStores()}
        >
          가게 목록 가져오기 (GET: /search/stores)
        </button>
        {stores && (
          <div className="w-full text-green-500">
            등록된 가게 정보: {JSON.stringify(stores)}
          </div>
        )}
      </div>

      {/* 특정 가게 가져오기 테스트 */}
      <div className="flex flex-col space-y-2 p-2 w-full p-2">
        <h2>특정 가게 가져오기 테스트</h2>
        {/* create product */}
        <button
          className={`bg-green-100 p-3 rounded-xl text-center cursor-pointer`}
          onClick={() => hadnleGetSpecificStore()}
        >
          특정 가게 가져오기 (GET: /search/stores/...)
        </button>
        {stores && (
          <div className="w-full text-green-500">
            등록된 가게 정보: {JSON.stringify(stores)}
          </div>
        )}
      </div>
    </div>
  );
};

export default CustomerLab;
