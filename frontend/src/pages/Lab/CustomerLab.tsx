// import { Outlet } from "react-router";
// import { useNavigate } from "react-router";

import type { PaymentConfirmType, PaymentResponseType } from "@interface";
import { getSpecificStore, getStores } from "@services";
import {
  cancelPayment,
  confrimPayment,
  initPayment,
} from "@services/customer/payment";
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
  const [confirm, setConfirm] = useState<PaymentConfirmType | null>(null);
  const [cancel, setCancel] = useState<PaymentConfirmType | null>(null);

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

  const handleConfrimPayment = async () => {
    if (!payment) return;
    try {
      const confirm = await confrimPayment({
        payment_id: payment.payment_id,
      });
      console.log("결제 확인 성공", confirm);
      setConfirm(confirm);
    } catch (err: unknown) {
      console.error("결제 확인 실패", payment);
      const msg = err instanceof Error ? err.message : "실패했슈...";
      setErrMsg(msg);
    }
  };

  const handleCancelPayment = async () => {
    if (!payment) return;
    try {
      const cancel = await cancelPayment(payment.payment_id);
      console.log("결제 취소 성공", cancel);
      setCancel(cancel);
    } catch (err: unknown) {
      console.error("");
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

      {/* err message */}
      {errMsg && <div className="text-red-600">{errMsg}</div>}

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

        {/* payment confirm */}
        <button
          className={`bg-green-200 p-3 rounded-xl text-center cursor-pointer`}
          onClick={() => handleConfrimPayment()}
        >
          결제 확인 (GET: /payment/confirm)
        </button>
        {payment && (
          <div className="w-full text-green-500">
            결제 확인: {JSON.stringify(confirm)}
          </div>
        )}

        {/* payment confirm */}
        <button
          className={`bg-green-300 p-3 rounded-xl text-center cursor-pointer`}
          onClick={() => handleCancelPayment()}
        >
          결제 취소 (GET: /payment/cancel)
        </button>
        {payment && (
          <div className="w-full text-green-500">
            결제 취소: {JSON.stringify(cancel)}
          </div>
        )}
      </div>
    </div>
  );
};

export default CustomerLab;
