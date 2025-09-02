import {
  createProduct,
  createStore,
  deleteStore,
  getStore,
  getStorePaymentStatus,
  getStoreProduct,
  registerStorePayment,
  updateStore,
} from "@services";
import PortOne from "@portone/browser-sdk/v2";
import { useEffect, useState } from "react";
import type {
  StorePaymentInfoResponseType,
  ProductRequestType,
  StoreResponseType,
  StoreWithProductResponseType,
  StorePaymentStatusType,
} from "@interface";
import type { PaymentStatusType, ItemType } from "@interface";

const SellerLab = () => {
  const [paymentStatus, setPaymentStatus] = useState<PaymentStatusType>({
    status: "IDLE",
  });

  // const [item, setItem] = useState(null);
  // dummy item
  const item: ItemType = {
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
    console.log("paymentStatus:", paymentStatus);
    const paymentId = randomId();
    const payment = await PortOne.requestPayment({
      storeId: "store-f7494ada-17a2-49c9-bb23-183d354afb27",
      channelKey: "channel-key-2bde6533-669f-4e5a-ae0c-5a471f10a463",
      paymentId,
      orderName: item.name,
      totalAmount: item.price,
      currency: item.currency,
      payMethod: "EASY_PAY",
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
  const [myProduct, setMyProduct] =
    useState<StoreWithProductResponseType | null>(null);
  const [StorePaymentStatus, setStorePaymentStatus] =
    useState<StorePaymentStatusType | null>(null);
  const [paymentInfo, setPaymentInfo] =
    useState<StorePaymentInfoResponseType | null>(null);

  /* err message */
  useEffect(() => {
    window.alert(errMsg);
  }, [errMsg]);

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

  // delete seller store
  const hadnleDeleteStore = async () => {
    if (!myStore) return;
    const ok = window.confirm("정말 이 가게를 삭제하실 건가요?");
    if (!ok) return;
    try {
      setErrMsg(null);
      await deleteStore(myStore.store_id);
      setMyStore(null);
      setStoreName("");
    } catch (err) {
      console.error("delete 실패", err);
      const msg = err instanceof Error ? err.message : "실패했슈...";
      setErrMsg(msg);
    }
  };

  // get store product
  const handleGetStoreProduct = async () => {
    if (!myStore) return;
    try {
      const myProduct = await getStoreProduct(myStore.store_id);
      console.log("get store product 성공", myProduct);
      setMyProduct(myProduct);
    } catch (err: unknown) {
      console.error("get store produc 실패", err);
      const msg = err instanceof Error ? err.message : "실패했슈...";
      setErrMsg(msg);
    }
  };

  // get store payment status info
  const handleGetStorePaymentStatus = async () => {
    if (!myStore) return;
    try {
      const storePaymentStatus = await getStorePaymentStatus(myStore.store_id);
      console.log("get store payment status 성공", storePaymentStatus);
      setStorePaymentStatus(storePaymentStatus);
    } catch (err: unknown) {
      console.error("get store produc 실패", err);
      const msg = err instanceof Error ? err.message : "실패했슈...";
      setErrMsg(msg);
    }
  };

  const [newProduct, setNewProduct] = useState<ProductRequestType | null>(null);

  // create seller product
  const handleCreateProduct = async () => {
    if (!myStore) return;
    try {
      const product = await createProduct({
        store_id: myStore.store_id,
        product_name: "행복조각",
        initial_stock: 10,
        price: 1004,
        sale: 50,
      });
      console.log("등록 성공:", newStore);
      setNewProduct(product);
    } catch (err: unknown) {
      console.error("등록 실패:", err);
      const msg = err instanceof Error ? err.message : "실패했슈...";
      setErrMsg(msg);
    }
  };

  // register payemnt info
  const handleRegisterPayment = async () => {
    try {
      const payment = await registerStorePayment("STR_1756784183_5a2b6928", {
        portone_store_id: "store-f7494ada-17a2-49c9-bb23-183d354afb27",
        portone_channel_id: "channel-key-2bde6533-669f-4e5a-ae0c-5a471f10a463",
        portone_secret_key:
          "jzfLikccL6YFl6ho9b38zylZXKFz9jh6jrxeowL6YDdDInnplMZZELVKx3VSsNaTmmB7IVk8KQxPBHLt",
      });
      setPaymentInfo(payment);
    } catch (err: unknown) {
      console.error("등록 실패:", err);
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
      <div className="flex flex-col space-y-2 p-2 w-full p-2">
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
                  <button
                    type="submit"
                    className="p-3 bg-orange-300 rounded-xl"
                  >
                    결제
                  </button>
                  <button className="p-3 bg-gray-300 rounded-xl">
                    새로고침
                  </button>
                </div>
              </>
            )}
          </div>
        </form>
      </div>

      {/* 가게 등록 테스트 */}
      <div className="flex flex-col space-y-2 p-2 w-full p-2">
        <h2>가게 등록 테스트</h2>

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

        {/* delete my store */}
        <button
          className={`bg-green-400 p-3 rounded-xl text-center cursor-pointer`}
          onClick={() => hadnleDeleteStore()}
        >
          가게 삭제하기 (DELETE: seller/stores)
        </button>
        {myStore && (
          <div className="w-full text-green-500">
            내 가게 정보: {JSON.stringify(myStore)}
          </div>
        )}

        {/* get store product */}
        <button
          className={`bg-green-500 p-3 rounded-xl text-center cursor-pointer`}
          onClick={() => handleGetStoreProduct()}
        >
          가게 물품 가져오기 (GET: seller/stores)
        </button>
        {myProduct && (
          <div className="w-full text-green-500">
            내 가게 물품 정보: {JSON.stringify(myProduct)}
          </div>
        )}

        {/* get store payment status */}
        <button
          className={`bg-green-500 p-3 rounded-xl text-center cursor-pointer`}
          onClick={() => handleGetStorePaymentStatus()}
        >
          가게 결제 정보 상태 확인 (GET: seller/stores)
        </button>
        {StorePaymentStatus && (
          <div className="w-full text-green-500">
            결제 정보 등록 상태: {JSON.stringify(StorePaymentStatus)}
          </div>
        )}

        {/* register payemnt info */}
        <button
          className={`bg-green-700 p-3 rounded-xl text-center cursor-pointer`}
          onClick={() => handleRegisterPayment()}
        >
          결제 정보 등록 (POST: seller/stores)
        </button>
        {paymentInfo && (
          <div className="w-full text-green-500">
            결제 정보: {JSON.stringify(paymentInfo)}
          </div>
        )}
      </div>

      {/* 물품 등록 테스트 */}
      <div className="flex flex-col space-y-2 p-2 w-full p-2">
        <h2>물품 등록 테스트</h2>
        {/* create product */}
        <button
          className={`bg-green-100 p-3 rounded-xl text-center cursor-pointer`}
          onClick={() => handleCreateProduct()}
        >
          물품 등록하기 (POST: seller/products)
        </button>
        {newStore && (
          <div className="w-full text-green-500">
            등록된 물품 정보: {JSON.stringify(newProduct)}
          </div>
        )}
      </div>
    </div>
  );
};

export default SellerLab;
