import { CommonModal } from "@components/common";
import type { StoreSearchBaseType } from "@interface";
import { GetFavoriteStore } from "@services";
import { formatErrMsg } from "@utils";
import { useEffect, useState } from "react";

const Favorite = () => {
  const [stores, setStores] = useState<StoreSearchBaseType>();
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

  useEffect(() => {
    handleGetFavorStore();
  }, []);

  if (!stores) {
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
    <>
      <div></div>
      {/* show modal */}
      {showModal && (
        <CommonModal
          desc={modalMsg}
          confirmLabel="확인"
          onConfirmClick={() => setShowModal(false)}
          category="black"
        />
      )}
    </>
  );
};

export default Favorite;
