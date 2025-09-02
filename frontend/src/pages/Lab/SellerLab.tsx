import {
  createProduct,
  createStore,
  deleteProduct,
  deleteStore,
  getStore,
  getStorePaymentStatus,
  getStoreProduct,
  registerStorePayment,
  updateProductPrice,
  updateProductStock,
  updateStore,
} from "@services";
import { useEffect, useState } from "react";
import type {
  StorePaymentInfoResponseType,
  ProductRequestType,
  StoreResponseType,
  StoreWithProductResponseType,
  StorePaymentStatusType,
} from "@interface";

const SellerLab = () => {
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
    console.error(errMsg);
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

  // update product price
  const handleUpdateProductPrice = async () => {
    if (!myProduct) return;
    try {
      const product = await updateProductPrice(
        myProduct.products[0].product_id,
        {
          product_name: myProduct.products[0].product_id,
          price: 9999,
          sale: 50,
        }
      );
      console.log("가격 업데이트 성공:", newStore);
      setNewProduct(product);
    } catch (err: unknown) {
      console.error("가격 업데이트 실패:", err);
      const msg = err instanceof Error ? err.message : "실패했슈...";
      setErrMsg(msg);
    }
  };

  // delete product
  const handleDeleteProduct = async () => {
    if (!myProduct) return;
    try {
      await deleteProduct(myProduct.products[0].product_id);
      console.log("상품 삭제 성공:", newStore);
    } catch (err: unknown) {
      console.error("상품 삭제 실패:", err);
      const msg = err instanceof Error ? err.message : "실패했슈...";
      setErrMsg(msg);
    }
  };

  // update product stock
  const handleUpdateProductStock = async () => {
    if (!myProduct) return;
    try {
      const product = await updateProductStock(
        myProduct.products[0].product_id,
        { stock: 10 }
      );
      console.log("상품 스톡 업데이트 성공:", product);
      setMyProduct(myProduct);
    } catch (err: unknown) {
      console.error("상품 스톡 업데이트 실패:", err);
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
        <h2>물품 테스트</h2>
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

        {/* update product price */}
        <button
          className={`bg-green-200 p-3 rounded-xl text-center cursor-pointer`}
          onClick={() => handleUpdateProductPrice()}
        >
          물품 가격 변경하기 (PUT: seller/products)
        </button>
        {newStore && (
          <div className="w-full text-green-500">
            수정된 물품 정보: {JSON.stringify(newProduct)}
          </div>
        )}

        {/* create product */}
        <button
          className={`bg-green-300 p-3 rounded-xl text-center cursor-pointer`}
          onClick={() => handleDeleteProduct()}
        >
          물품 삭제하기 (DELETE: seller/products)
        </button>
        {newStore && (
          <div className="w-full text-green-500">
            삭제된 물품 정보: {JSON.stringify(newProduct)}
          </div>
        )}

        {/* update product stock */}
        <button
          className={`bg-green-400 p-3 rounded-xl text-center cursor-pointer`}
          onClick={() => handleUpdateProductStock()}
        >
          물품 수량 변경 (PATCH: seller/products)
        </button>
        {newStore && (
          <div className="w-full text-green-500">
            변경된 물품 정보: {JSON.stringify(newProduct)}
          </div>
        )}
      </div>
    </div>
  );
};

export default SellerLab;
