import { CommonModal } from "@components/common";
import { StoreBox } from "@components/customer/storeList";
import type { StoreSearchBaseType } from "@interface";
import {
  AddFavoriteStore,
  GetFavoriteStore,
  RemoveFavoriteStore,
} from "@services";
import { formatErrMsg } from "@utils";
import { useEffect, useState } from "react";

const Favorite = () => {
  const [stores, setStores] = useState<StoreSearchBaseType[]>();
  const [showModal, setShowModal] = useState<boolean>(false);
  const [modalMsg, setModalMsg] = useState("");

  const handleGetFavorStore = async () => {
    try {
      const res = await GetFavoriteStore();
      setStores(res);
      console.log(stores);
    } catch (err) {
      setModalMsg(formatErrMsg(err));
      setShowModal(true);
    }
  };

  // add or delete favorite store
  const handleUpdateFavorStore = async (storeId: string, nowFavor: boolean) => {
    try {
      if (!nowFavor) {
        // add favor store
        await AddFavoriteStore(storeId);
      } else {
        // remove favor store
        await RemoveFavoriteStore(storeId);
      }

      const updated = await GetFavoriteStore();
      setStores(updated);
    } catch (err) {
      setModalMsg("선호 가게 업데이트에 실패했습니다.");
      setShowModal(true);
    }
  };

  useEffect(() => {
    handleGetFavorStore();
  }, []);

  if (!stores || stores.length === 0) {
    return (
      <div className="flex flex-col w-full h-full justify-center items-center">
        <img
          src="/icon/saladBowl.svg"
          alt="saladBowlIcon"
          className="pb-[26px] w-[116px]"
        />
        <div className="text-[20px] pb-[17px] font-bold">
          아직 관심 가게가 없어요.
        </div>
        <div className="text-[12px] font-base">
          다양한 가게를 확인하고 주문해보세요.
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col px-[20px]">
      <div className="flex flex-col gap-y-[10px] justify-center">
        <StoreBox stores={stores} onToggleFavorite={handleUpdateFavorStore} />
      </div>

      {/* show modal */}
      {showModal && (
        <CommonModal
          desc={modalMsg}
          confirmLabel="확인"
          onConfirmClick={() => setShowModal(false)}
          category="black"
        />
      )}
    </div>
  );
};

export default Favorite;
