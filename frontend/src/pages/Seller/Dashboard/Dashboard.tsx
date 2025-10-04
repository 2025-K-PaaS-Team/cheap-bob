import { CommonModal } from "@components/common";
import {
  NowOpStatus,
  RemainPkg,
  StoreManage,
} from "@components/seller/dashboard";
import type { DashboardResponseType, StoreDetailType } from "@interface";
import { GetStoreDetail } from "@services";
import { GetDashboard } from "@services/seller/order";
import { useDashboardStore } from "@store";
import { formatErrMsg } from "@utils";
import { useEffect, useState } from "react";

const Dashboard = () => {
  const [data, setData] = useState<StoreDetailType | null>(null);
  const [remainPkg, setRemainPkg] = useState<DashboardResponseType | null>(
    null
  );
  const [showModal, setShowModal] = useState<boolean>(false);
  const [modalMsg, setModalMsg] = useState("");
  // 가게 별 패키지 1개 제한 수정 후 제거 필요
  const repPkg = (remainPkg?.items ?? [])
    .slice()
    .sort((a, b) => a.product_id.localeCompare(b.product_id))[0];
  const setRepProductId = useDashboardStore((s) => s.setRepProductId);

  const handleGetStore = async () => {
    try {
      const res = await GetStoreDetail();
      setData(res);
    } catch (err) {
      setModalMsg(formatErrMsg(err));
      setShowModal(true);
    }
  };

  const handleGetDashboard = async () => {
    try {
      const res = await GetDashboard();
      setRemainPkg(res);
    } catch (err) {
      setModalMsg(formatErrMsg(err));
      setShowModal(true);
    }
  };

  useEffect(() => {
    handleGetStore();
    handleGetDashboard();
  }, []);

  useEffect(() => {
    if (repPkg?.product_id) setRepProductId(repPkg.product_id);
    else setRepProductId(null);
  }, [repPkg?.product_id, setRepProductId]);

  if (!data) {
    return <div>로딩중...</div>;
  }
  return (
    <div className="flex w-full flex-col">
      {/* now operating status */}
      <NowOpStatus ops={data.operation_times} />

      {/* remaining package quantity */}
      <RemainPkg
        remainPkg={repPkg ?? []}
        setShowModal={setShowModal}
        setModalMsg={setModalMsg}
        onChanged={handleGetDashboard}
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
