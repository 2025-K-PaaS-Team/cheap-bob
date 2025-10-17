import { CommonModal } from "@components/common";
import type { StoreDetailType } from "@interface";
import {
  GetStoreDetail,
  GetStoreWeekSettlement,
  WithdrawCustomer,
  WithdrawSeller,
} from "@services";
import { formatErrMsg } from "@utils";
import dayjs from "dayjs";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router";

const BillingInfo = () => {
  const navigate = useNavigate();
  const [weekRevenue, setWeekRevenue] = useState<number>(0);
  const [showModal, setShowModal] = useState<boolean>(false);
  const [modalMsg, setModalMsg] = useState("");
  const [store, setStore] = useState<StoreDetailType | null>(null);
  const [showWarn, setShowWarn] = useState<Boolean>(false);
  const today = dayjs();
  const endDate = today.add(-6, "day");

  const handleGetWeekBilling = async () => {
    try {
      const res = await GetStoreWeekSettlement();
      setWeekRevenue(res.total_revenue);
    } catch (err) {
      setModalMsg(formatErrMsg(err));
      setShowModal(true);
      return;
    }
  };

  const handleGetStore = async () => {
    try {
      const res = await GetStoreDetail();
      setStore(res);
    } catch (err) {
      setModalMsg(formatErrMsg(err));
      setShowModal(true);
      return;
    }
  };

  const handlePostWithdraw = async () => {
    setShowWarn(false);
    try {
      await WithdrawCustomer();
      navigate("withdraw");
    } catch (err) {
      setModalMsg(formatErrMsg(err));
      setShowModal(true);
      return;
    }
  };

  useEffect(() => {
    handleGetWeekBilling();
    handleGetStore();
  }, []);

  return (
    <div className="flex flex-col relative h-full">
      {/* top content */}
      <div className="mx-[20px]">
        {/* greeting */}
        <div className="flex flex-col pb-[31.5px] gap-y-[10px]">
          <div className="titleFont">{store?.store_name} 님, 안녕하세요.</div>
          <div className="bodyFont">{store?.seller_email}</div>
        </div>
        {/* total revenue */}
        <div className="flex flex-col bg-main-pale border border-main-deep rounded text-custom-black px-[16px] py-[20px] gap-y-[5px]">
          <h1>이번 주 수익</h1>
          <div className="hintFont">
            {endDate.format("YYYY.MM.DD")} ~ {today.format("MM.DD")}
          </div>
          <h2>{weekRevenue ?? 0} 원</h2>
        </div>
      </div>

      {/* bottom content */}
      <div className="absolute bottom-5 w-full max-w-[420px] py-[20px] border-t border-black/10">
        <div className="mx-[20px]">
          {/* history */}
          <div
            onClick={() => navigate("history")}
            className="bodyFont font-bold py-[20px] flex flex-row justify-between border-b border-black/10"
          >
            <div>정산 내역 보기</div>
            <div>&gt;</div>
          </div>
          {/* change billing info */}
          <div
            className="bodyFont font-bold py-[20px] flex flex-row justify-between border-b border-black/10"
            onClick={() => navigate("change")}
          >
            <div>정산 정보 변경</div>
            <div>&gt;</div>
          </div>
          {/* help */}
          <div className="bodyFont font-bold py-[20px] flex flex-row justify-between border-b border-black/10">
            <div>도움말</div>
            <div>&gt;</div>
          </div>
          {/* logout */}
          <div className="bodyFont font-bold py-[20px] border-b border-black/10">
            <div onClick={() => navigate("/s")}>로그아웃</div>
          </div>
          {/* withdraw */}
          <div
            className="bodyFont font-bold text-sub-red py-[20px]"
            onClick={() => setShowWarn(true)}
          >
            <div>계정 탈퇴</div>
          </div>
        </div>
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

      {/* show warn modal */}
      {showWarn && (
        <CommonModal
          desc="계정 탈퇴 시, <b>가게 정보는 유지</b>되지만<br/> <b>가게가 더이상 타 사용자에게 노출되지 않습니다.</b> <br/> <br/> 탈퇴하시겠습니까?"
          confirmLabel="네, 탈퇴합니다."
          onConfirmClick={handlePostWithdraw}
          onCancelClick={() => setShowWarn(false)}
          category="red"
          className="text-start"
        />
      )}
    </div>
  );
};

export default BillingInfo;
