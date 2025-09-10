import type { StoreResponseType } from "@interface";
import { getStore, updateStore } from "@services";
import { useEffect, useState } from "react";
import { formatDate } from "@utils";

const Store = () => {
  const [myStore, setMyStore] = useState<StoreResponseType | null>(null);
  const [storeName, setStoreName] = useState<string>("");

  const handleGetStore = async () => {
    try {
      const res = await getStore();
      console.log("handleGetStore 성공", res);
      setMyStore(res);
    } catch (err) {
      console.error("handleGetStore 실패", err);
    }
  };

  useEffect(() => {
    handleGetStore();
  }, []);

  if (!myStore) {
    return (
      <>
        <div>가게가 없으시네요...</div>
        <button>내 가게 등록하기</button>
      </>
    );
  }

  const hadnleUpdateStore = async () => {
    const name = storeName?.trim();
    if (!name) {
      window.alert("가게 이름은 공란xx");
    }

    try {
      await updateStore(myStore.store_id, { store_name: name });
    } catch (err) {
      console.error("udpate 실패", err);
    }
  };

  return (
    <div className="bg-green-200 p-3 m-3">
      <div>내 가게 이름: {myStore.store_name}</div>
      <div>이메일: {myStore.seller_email}</div>
      <div>내 가게 생성 일자: {formatDate(myStore.created_at)}</div>
      {/* update my store */}
      <button
        className={`bg-white p-3 text-center cursor-pointer`}
        onClick={() => hadnleUpdateStore()}
      >
        가게 정보 업데이트
      </button>
      {myStore && (
        <>
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

export default Store;
