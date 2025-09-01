import { createStore, getStore, updateStore } from "@services";
import PortOne from "@portone/browser-sdk/v2";
import { useEffect, useState } from "react";
import type { StoreResponseType } from "@interface";

const SellerLab = () => {
  type PaymentStatus = {
    status: "IDLE" | "PENDING" | "SUCCESS" | "FAILED";
    message?: string;
    code?: string;
  };

  type item = {
    id: number;
    name: string;
    price: number;
    currency: "KRW";
    currencyLabel: "원";
    img: string;
  };

  const [paymentStatus, setPaymentStatus] = useState<PaymentStatus>({
    status: "IDLE",
  });

  // build 에러 방지용 임시 콘솔
  console.log(paymentStatus);

  // const [item, setItem] = useState(null);
  // dummy item
  const item: item = {
    id: 1219,
    name: "행복한하루",
    price: 1000,
    currency: "KRW",
    currencyLabel: "원",
    img: "https://velog.velcdn.com/images/gimgyuwon/profile/e18f35d4-46dd-4ea7-859a-53bfaaad629b/image.png",
  };

  const randomId = () => {
    return [...crypto.getRandomValues(new Uint32Array(2))]
      .map((word) => word.toString(16).padStart(8, "0"))
      .join("");
  };

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setPaymentStatus({ status: "PENDING" });
    const paymentId = randomId();
    const payment = await PortOne.requestPayment({
      storeId: "store-368b20a0-d0e0-4770-bf3e-0b51eaa97466",
      channelKey: "channel-key-9d9848fb-cd40-4dba-a157-33089c0fb971",
      paymentId,
      orderName: item.name,
      totalAmount: item.price,
      currency: item.currency,
      payMethod: "CARD",
      customer: {
        fullName: "김규원",
        email: "gimgyuwon2@gmail.com",
        phoneNumber: "01086910510",
      },
      customData: {
        item: item.id,
      },
    });

    if (!payment) {
      setPaymentStatus({ status: "FAILED" });
      return;
    }

    // 실패 케이스
    if (payment.code !== undefined) {
      setPaymentStatus({
        status: "FAILED",
        message: payment?.message,
      });
    }
  };

  const [errMsg, setErrMsg] = useState<string | null>(null);
  const [newStore, setNewStore] = useState<StoreResponseType | null>(null);
  const [myStore, setMyStore] = useState<StoreResponseType | null>(null);
  const [storeName, setStoreName] = useState<string>("");

  // create seller store
  const handleCreateStore = async () => {
    try {
      const store = await createStore({ store_name: "test store name" });
      console.log("등록 성공:", newStore);
      setNewStore(store);
    } catch (err: unknown) {
      console.error("등록 실패:", err);
      const msg = err instanceof Error ? err.message : "실패했슈...";
      setErrMsg(msg);
    }
  };

  // get seller store
  const handleGetStore = async () => {
    try {
      const store = await getStore();
      setMyStore(store);
      console.log("get 성공", myStore);
    } catch (err) {
      console.error("get 실패", err);
      const msg = err instanceof Error ? err.message : "실패했슈...";
      setErrMsg(msg);
    }
  };

  // udpate seller store
  const hadnleUpdateStore = async () => {
    if (!myStore) return;
    const name = storeName?.trim();
    if (!name) {
      setErrMsg("가게 이름을 입력해주세요");
      return;
    }

    try {
      await updateStore(myStore.store_id, { store_name: name });
    } catch (err) {
      console.error("udpate 실패", err);
      const msg = err instanceof Error ? err.message : "실패했슈...";
      setErrMsg(msg);
    }
  };

  // my store 바뀔 때 store name도 업데이트
  useEffect(() => {
    if (myStore) setStoreName(myStore.store_name);
  }, [myStore]);

  return (
    <div className="min-h-screen m-5 gap-y-2 flex flex-col justify-center items-center">
      {/* 결제 테스트 */}
      <h2>결제 테스트</h2>
      <form onSubmit={handleSubmit}>
        <div className="rounded-xl w-full bg-yellow-200 p-3">
          {!item ? (
            <div>결제 정보를 불러오는 중입니다.</div>
          ) : (
            <>
              {" "}
              <div className="font-bold">{item.name}</div>
              <img src={item.img} alt="" />
              <div>
                {item.price}
                {item.currencyLabel}
              </div>
              <div className="flex flex-row gap-x-5">
                <button type="submit" className="p-3 bg-orange-300 rounded-xl">
                  결제
                </button>
                <button className="p-3 bg-gray-300 rounded-xl">새로고침</button>
              </div>
            </>
          )}
        </div>
      </form>

      {/* 가게 등록 테스트 */}
      <h2>가게 등록 테스트</h2>

      {/* err message */}
      {errMsg && <div className="text-red-600">{errMsg}</div>}

      {/* create store */}
      <button
        className={`bg-green-100 p-3 rounded-xl text-center cursor-pointer`}
        onClick={() => handleCreateStore()}
      >
        가게 등록하기 (POST: seller/stores)
      </button>
      {newStore && (
        <div className="w-full text-green-500">
          등록된 가게 정보: {JSON.stringify(newStore)}
        </div>
      )}

      {/* get my store */}
      <button
        className={`bg-green-200 p-3 rounded-xl text-center cursor-pointer`}
        onClick={() => handleGetStore()}
      >
        가게 정보 가져오기 (GET: seller/stores)
      </button>
      {myStore && (
        <div className="w-full text-green-500">
          내 가게 정보: {JSON.stringify(myStore)}
        </div>
      )}

      {/* update my store */}
      <button
        className={`bg-green-300 p-3 rounded-xl text-center cursor-pointer`}
        onClick={() => hadnleUpdateStore()}
      >
        가게 정보 업데이트 (PUT: seller/stores)
      </button>
      {myStore && (
        <>
          <div className="w-full text-green-500 text-center">
            업데이트 할 가게 이름을 입력하소
          </div>
          <input
            type="text"
            className="border-2 border-green-500 p-2"
            placeholder="업데이트 할 가게 이름을 입력하쇼"
            value={storeName}
            onChange={(e) => setStoreName(e.target.value)}
          />
          <button
            onClick={() => hadnleUpdateStore()}
            className={`bg-green-300 p-3 rounded-xl text-center cursor-pointer`}
          >
            저장하수
          </button>
        </>
      )}
    </div>
  );
};

export default SellerLab;
