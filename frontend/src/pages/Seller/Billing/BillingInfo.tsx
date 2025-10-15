import { CommonModal } from "@components/common";
import { GetStoreWeekSettlement } from "@services";
import { formatErrMsg } from "@utils";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router";

const BillingInfo = () => {
  const navigate = useNavigate();
  const [weekRevenue, setWeekRevenue] = useState<number>(0);
  const [showModal, setShowModal] = useState<boolean>(false);
  const [modalMsg, setModalMsg] = useState("");

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

  useEffect(() => {
    handleGetWeekBilling();
  }, []);

  return (
    <div>
      <div className="text-[24px] mx-[37px]">
        <div>이번 주 수익</div>
        <div>{weekRevenue ?? 0} 원</div>
        <div
          className="mt-[10px] text-custom-black/80 text-[18px]"
          onClick={() => navigate("history")}
        >
          정산 내역 보기 &gt;
        </div>

        <hr className="h-[1px] border-0 bg-black/20 mb-[44px] mt-[369px]" />

        {/* change billing info */}
        <div
          className="text-[16px] font-bold py-[20px] flex flex-row justify-between"
          onClick={() => navigate("change")}
        >
          <div>정산 정보 변경</div>
          <div>&gt;</div>
        </div>
        {/* help */}
        <div className="text-[16px] font-bold py-[20px] flex flex-row justify-between">
          <div>도움말</div>
          <div>&gt;</div>
        </div>
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

export default BillingInfo;
