// import { Outlet } from "react-router";
// import { useNavigate } from "react-router";

import { PaymentResponseType } from "@interface";
import { getSpecificStore, getStores } from "@services";
import { initPayment } from "@services/customer/payment";
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

  const [payment, setPayment] = useState<PaymentResponseType | null>(null);

  const handleInitPayment = async () => {
    try {
      const payment = await initPayment({
        product_id: "PRD_1756712045_97763a9d",
        quantity: 1,
      });
      console.log("초기화 성공", payment);
      setPayment(payment);
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

      {/* 가게 검색 테스트 */}
      <div className="flex flex-col space-y-2 p-2 w-full p-2">
        <h2>가게 검색 테스트</h2>
        {/* get stores */}
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

        {/* get specific store */}
        <button
          className={`bg-green-200 p-3 rounded-xl text-center cursor-pointer`}
          onClick={() => hadnleGetSpecificStore()}
        >
          특정 가게 가져오기 (GET: /search/stores/...)
        </button>
        {store && (
          <div className="w-full text-green-500">
            등록된 가게 정보: {JSON.stringify(store)}
          </div>
        )}
      </div>

      {/* 결제 테스트 */}
      <div className="flex flex-col space-y-2 p-2 w-full p-2">
        <h2>결제 테스트</h2>
        {/* payment init */}
        <button
          className={`bg-green-100 p-3 rounded-xl text-center cursor-pointer`}
          onClick={() => handleInitPayment()}
        >
          결제 초기화 (GET: /payment/init)
        </button>
        {payment && (
          <div className="w-full text-green-500">
            결제 정보: {JSON.stringify(payment)}
          </div>
        )}
      </div>
    </div>
  );
};

export default CustomerLab;
