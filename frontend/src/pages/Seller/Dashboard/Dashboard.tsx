import {
  NowOpStatus,
  RemainPkg,
  StoreManage,
} from "@components/seller/dashboard";
import { GetStoreDetail } from "@services";
import { useEffect } from "react";

const Dashboard = () => {
  useEffect(() => {
    GetStoreDetail();
  }, []);

  return (
    <div className="flex w-full flex-col">
      {/* now operating status */}
      <NowOpStatus />

      {/* remaining package quantity */}
      <RemainPkg />

      {/* border */}
      <hr className="bg-black/20 h-[1px] border-0 mt-[50px] mb-[33px]" />

      {/* my store info */}
      <StoreManage />
    </div>
  );
};

export default Dashboard;
