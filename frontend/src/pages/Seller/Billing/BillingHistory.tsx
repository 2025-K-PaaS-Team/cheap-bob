import { CommonModal } from "@components/common";
import { BillingStatus } from "@components/seller/billing";
import type { SettlementType } from "@interface";
import { GetStoreSettlement } from "@services";
import dayjs from "dayjs";
import { useEffect, useState } from "react";

const BillingHistory = () => {
  const endDate = dayjs();
  const startDate = endDate.add(-1, "month");
  const [status, setStatus] = useState<string>("all");
  const [settlement, setSettlement] = useState<SettlementType | null>(null);
  const [showModal, setShowModal] = useState<boolean>(false);
  const [modalMsg, setModalMsg] = useState("");

  const handleGetSettlement = async (start: string, end: string) => {
    try {
      const res = await GetStoreSettlement(start, end);
      setSettlement(res);
    } catch (err: unknown) {
      setModalMsg("정산 내역을 불러오는데 실패했습니다.");
      setShowModal(true);
    }
  };

  useEffect(() => {
    handleGetSettlement(
      startDate.format("YYYY-MM-DD"),
      endDate.format("YYYY-MM-DD")
    );
  }, []);

  if (!settlement) {
    return <div>로딩 중...</div>;
  }

  return (
    <div className="flex flex-col relative h-full">
      <div className="mx-[33px] flex flex-col gap-y-[15px] mt-[15px]">
        {/* period */}
        <div className="flex flex-row text-center gap-x-[10px]">
          <div className="fontBody font-bold mr-auto">기간</div>
          <div className="border-b border-black/80 w-[103px] h-[30px] text-custom-black">
            {startDate.format("YYYY.MM.DD")}
          </div>
          <div className="fontBody font-bold">~</div>
          <div className="border-b border-black/80 w-[103px] h-[30px] text-custom-black">
            {endDate.format("YYYY.MM.DD")}
          </div>
        </div>

        {/* billing status */}
        <BillingStatus nowStatus={status} setNowStatus={setStatus} />
      </div>

      {/* divider */}
      <hr className="border-0 h-[1px] bg-black/20 mt-[35px]" />

      {/* order history */}
      <div className="flex flex-col flex-1 p-[20px] gap-y-[20px] bg-custom-white">
        <div className="hintFont">
          <span className="text-main-deep">
            {settlement?.daily_settlements[0]?.items[0]?.total_amount ?? 0}
          </span>
          건의 주문 내역이 있습니다.
        </div>
        <div className="text-[16px] font-bold">25.09.08</div>
        <div className="bg-white shadow rounded px-[17px] py-[20px] text-[16px] gap-y-[7px] flex flex-col">
          <div className="justify-between flex-row flex">
            <div className="font-bold">(패키지 이름)</div>
            <div>1개</div>
          </div>
          <div className="justify-between flex-row flex">
            <div>환불 완료</div>
            <div>0,000원</div>
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
    </div>
  );
};

export default BillingHistory;
