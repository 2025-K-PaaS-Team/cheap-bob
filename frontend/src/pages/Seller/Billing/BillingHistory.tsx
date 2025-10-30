import { CommonModal } from "@components/common";
import CommonLoading from "@components/common/CommonLoading";
import { BillingStatus } from "@components/seller/billing";
import type { SettlementType } from "@interface";
import { GetStoreSettlement } from "@services";
import dayjs from "dayjs";
import { useEffect, useMemo, useState } from "react";

const BillingHistory = () => {
  const [endDate, setEndDate] = useState(dayjs());
  const [startDate, setStartDate] = useState(dayjs().add(-1, "month"));
  const [status, setStatus] = useState<string>("all");
  const [settlement, setSettlement] = useState<SettlementType | null>(null);
  const [showModal, setShowModal] = useState<boolean>(false);
  const [modalMsg, setModalMsg] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleGetSettlement = async (start: string, end: string) => {
    try {
      const res = await GetStoreSettlement(start, end);
      setSettlement(res);
    } catch (err: unknown) {
      setModalMsg("정산 내역을 불러오는데 실패했습니다.");
      setShowModal(true);
    }
  };

  const filteredSettlements = useMemo(() => {
    if (!settlement) return [];

    if (status === "all") return settlement.daily_settlements;

    return settlement.daily_settlements
      .map((day) => ({
        ...day,
        items: day.items.filter((item) => {
          if (status === "complete") return item.status === "complete";
          if (status === "cancel") return item.status === "cancel";
          return true;
        }),
      }))
      .filter((day) => day.items.length > 0);
  }, [settlement, status]);

  const totalCount = useMemo(() => {
    return filteredSettlements.reduce((sum, day) => sum + day.items.length, 0);
  }, [filteredSettlements]);

  useEffect(() => {
    const init = async () => {
      await handleGetSettlement(
        startDate.format("YYYY-MM-DD"),
        endDate.format("YYYY-MM-DD")
      );
      setIsLoading(false);
    };
    init();
  }, [startDate, endDate]);

  if (isLoading) {
    return <CommonLoading type="data" isLoading={isLoading} />;
  }

  return (
    <div className="flex flex-col relative h-full">
      {/* Header */}
      <div className="mx-[33px] flex flex-col gap-y-[15px] mt-[15px]">
        {/* 기간 선택 */}
        <div className="flex items-center gap-x-[5px] text-nowrap">
          <div className="fontBody font-bold mr-auto">기간</div>
          <input
            type="date"
            value={startDate.format("YYYY-MM-DD")}
            onChange={(e) => setStartDate(dayjs(e.target.value))}
            onFocus={(e) => e.target.showPicker()}
            className="w-[110px] h-[36px] pl-5 text-center flex items-center justify-center border-b border-black/80 hintFont focus:outline-none appearance-none [&::-webkit-calendar-picker-indicator]:hidden cursor-pointer"
          />

          <span className="fontBody font-bold">~</span>
          <input
            type="date"
            value={endDate.format("YYYY-MM-DD")}
            onChange={(e) => setEndDate(dayjs(e.target.value))}
            onFocus={(e) => e.target.showPicker()}
            className="w-[110px] h-[36px] pl-5 text-center flex items-center justify-center border-b border-black/80 hintFont focus:outline-none appearance-none [&::-webkit-calendar-picker-indicator]:hidden cursor-pointer"
          />
        </div>

        {/* 상태 선택 */}
        <BillingStatus nowStatus={status} setNowStatus={setStatus} />
      </div>

      {/* divider */}
      <hr className="border-0 h-[1px] bg-black/20 mt-[35px]" />

      {/* order history */}
      <div className="flex flex-col flex-1 p-[20px] gap-y-[20px] bg-custom-white overflow-y-auto">
        <div className="hintFont">
          총 <span className="text-main-deep font-bold">{totalCount}</span>건의
          주문 내역이 있습니다.
        </div>

        {filteredSettlements.map((day) => (
          <div key={day.date} className="flex flex-col gap-y-[10px]">
            <div className="text-[16px] font-bold mt-[10px]">
              {dayjs(day.date).format("YY.MM.DD")}
            </div>

            {day.items.map((item, idx) => (
              <div
                key={`${day.date}-${idx}`}
                className="bg-white shadow rounded p-[16px] text-[16px] flex flex-col gap-y-[10px]"
              >
                <div className="flex justify-between">
                  <h3>{item.time_at}</h3>
                  <div>
                    주문 수량:{" "}
                    <span className="font-bold text-main-deep">
                      {item.quantity}
                    </span>
                    개
                  </div>
                </div>

                <div className="flex justify-between bodyFont">
                  <div
                    className={`font-bold ${
                      item.status === "cancel"
                        ? "text-sub-orange"
                        : "text-main-deep"
                    }`}
                  >
                    {item.status === "complete"
                      ? "정산 완료"
                      : item.status === "cancel"
                      ? "환불 완료"
                      : item.status}
                  </div>
                  <div>{item.total_amount.toLocaleString()}원</div>
                </div>
              </div>
            ))}
          </div>
        ))}

        {filteredSettlements.length === 0 && (
          <div className="text-center text-sm text-gray-400 mt-5">
            해당 상태의 정산 내역이 없습니다.
          </div>
        )}
      </div>

      {/* modal */}
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
