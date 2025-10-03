import { CommonModal } from "@components/common";
import {
  NowOpStatus,
  RemainPkg,
  StoreManage,
} from "@components/seller/dashboard";
import type { StoreDetailType } from "@interface";
import { GetStoreDetail } from "@services";
import { formatErrMsg } from "@utils";
import { useEffect, useState } from "react";

const Dashboard = () => {
  const [data, setData] = useState<StoreDetailType | null>(null);
  const [showModal, setShowModal] = useState<boolean>(false);
  const [modalMsg, setModalMsg] = useState("");
  const repProduct = (data?.products ?? [])
    .slice()
    .sort((a, b) => a.product_id.localeCompare(b.product_id))[0];

  const handleGetStore = async () => {
    try {
      const res = await GetStoreDetail();
      setData(res);
    } catch (err) {
      setModalMsg(formatErrMsg(err));
      setShowModal(true);
    }
  };

  useEffect(() => {
    handleGetStore();
  }, []);

  if (!data) {
    return <div>로딩중...</div>;
  }
  return (
    <div className="flex w-full flex-col">
      {/* now operating status */}
      <NowOpStatus />

      {/* remaining package quantity */}
      <RemainPkg
        product={repProduct ?? []}
        setShowModal={setShowModal}
        setModalMsg={setModalMsg}
        onChanged={handleGetStore}
      />

      {/* border */}
      <hr className="bg-black/20 h-[1px] border-0 mt-[50px] mb-[33px]" />

      {/* my store info */}
      <StoreManage />

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

export default Dashboard;
