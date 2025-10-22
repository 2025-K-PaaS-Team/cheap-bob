import { CommonBtn, CommonModal } from "@components/common";
import CommonLoading from "@components/common/CommonLoading";
import { StoreBox } from "@components/customer/storeList";
import type { StoreSearchBaseType } from "@interface";
import {
  AddFavoriteStore,
  GetFavoriteStore,
  RemoveFavoriteStore,
} from "@services";
import { formatErrMsg } from "@utils";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

const Favorite = () => {
  const navigate = useNavigate();
  const [stores, setStores] = useState<StoreSearchBaseType[]>();
  const [showModal, setShowModal] = useState<boolean>(false);
  const [modalMsg, setModalMsg] = useState("");
  const [isLoading, setIsLoading] = useState<boolean>(true);

  const handleGetFavorStore = async () => {
    try {
      const res = await GetFavoriteStore();
      setStores(res);
    } catch (err) {
      setModalMsg(formatErrMsg(err));
      setShowModal(true);
    } finally {
      setIsLoading(false);
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

  if (isLoading) {
    return <CommonLoading type="data" isLoading={isLoading} />;
  }

  if (!stores || stores.length === 0) {
    return (
      <div className="flex flex-col h-full justify-center items-center bg-custom-white">
        <img
          src="/icon/angrySalad.svg"
          alt="saladBowlIcon"
          className="pb-[26px] w-[116px]"
        />
        <div className="text-[20px] pb-[17px] font-bold">
          관심 가게가 비어있어요.
        </div>
        <div className="text-[12px] font-base pb-[46px]">
          다양한 랜덤팩을 주문하고 픽업해보세요.
        </div>
        <CommonBtn
          label="실시간 랜덤팩 보러가기"
          notBottom
          width="w-[calc(100%-40px)]"
          onClick={() => navigate("/c/stores")}
        />
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
          category="green"
        />
      )}
    </div>
  );
};

export default Favorite;
