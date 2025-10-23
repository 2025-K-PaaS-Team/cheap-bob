import { CommonModal } from "@components/common";
import CommonLoading from "@components/common/CommonLoading";
import { idxToDow } from "@constant";
import type { StoreOperationType } from "@interface";
import { GetStoreOperation, GetStoreOpReservation } from "@services";
import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";

const hhmm = (t?: string) => (t ? t.slice(0, 5) : "—");
const pickDefaultDow = (ops: StoreOperationType): number | null => {
  const active = ops.filter((o) => o.is_open_enabled);
  if (active.length === 0) return null;
  return active.slice().sort((a, b) => a.day_of_week - b.day_of_week)[0]
    .day_of_week;
};

const ChangeOperationInfo = () => {
  const navigate = useNavigate();
  const items = [
    { label: "영업 시간 변경", to: "/s/change/operation/op-time" },
    { label: "픽업 시간 변경", to: "/s/change/operation/pu-time" },
  ];

  const [op, setOp] = useState<StoreOperationType>([]);
  const [reservation, setReservation] = useState([]);
  const [selectedDow, setSelectedDow] = useState<number | null>(null);
  const [showModal, setShowModal] = useState(false);
  const [modalMsg, setModalMsg] = useState("");
  const [isLoading, setIsLoading] = useState<boolean>(true);

  const activeDays = useMemo(() => op.filter((o) => o.is_open_enabled), [op]);

  const selectedOp = useMemo(() => {
    if (selectedDow == null) return undefined;
    return op.find((o) => o.is_open_enabled && o.day_of_week === selectedDow);
  }, [op, selectedDow]);

  const handleGetStoreOperation = async () => {
    try {
      const res = await GetStoreOperation();
      setOp(res);
      setSelectedDow(pickDefaultDow(res));
    } catch {
      setModalMsg("운영 정보를 불러오는 것에 실패했습니다.");
      setShowModal(true);
    } finally {
      setIsLoading(false);
    }
  };

  const handleGetStoreReservation = async () => {
    try {
      const res = await GetStoreOpReservation();
      setReservation(res.modifications);
    } catch {
      setModalMsg("운영 변경 예약 정보를 불러오는 것에 실패했습니다.");
      setShowModal(true);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    handleGetStoreOperation();
    handleGetStoreReservation();
  }, []);

  if (isLoading) {
    return <CommonLoading type="data" isLoading={isLoading} />;
  }

  return (
    <div className="mx-[35px]">
      <div className="flex flex-col gap-y-[10px]">
        <h3 className="py-[10px]">현재 영업 시간</h3>

        {/* 영업 요일: 활성 요일만 */}

        <div className="flex flex-row justify-around hint">
          {activeDays.length === 0 ? (
            <div className="text-custom-black/50">
              영업 중인 요일이 없습니다
            </div>
          ) : (
            activeDays.map((day) => {
              const dow = day.day_of_week;
              const isSelected = selectedDow === dow;
              return (
                <button
                  key={dow}
                  type="button"
                  className={`font-bold hintFont w-[32px] h-[32px] rounded-full flex items-center justify-center
                      ${
                        isSelected
                          ? "bg-main-deep text-white"
                          : "bg-custom-white text-custom-black"
                      }`}
                  onClick={() => setSelectedDow(dow)}
                  aria-pressed={isSelected}
                  title={idxToDow[dow]}
                >
                  {idxToDow[dow]}
                </button>
              );
            })
          )}
        </div>

        {/* 선택된 요일의 시간 */}
        <div className="bg-[#E7E7E7] hintFont rounded-sm my-[8px] flex flex-col py-[15px] px-[23px] space-y-[10px]">
          {selectedOp ? (
            <>
              <div className="flex flex-row">
                <div className="w-[120px]">오픈 시간</div>
                <div className="text-center">{hhmm(selectedOp.open_time)}</div>
              </div>
              <div className="flex flex-row">
                <div className="w-[120px]">픽업 확정 시간</div>
                <div className="text-center">
                  {hhmm(selectedOp.pickup_start_time)}
                </div>
              </div>
              <div className="flex flex-row">
                <div className="w-[120px]">픽업 마감 시간</div>
                <div className="text-center">
                  {hhmm(selectedOp.pickup_end_time)}
                </div>
              </div>
              <div className="flex flex-row">
                <div className="w-[120px]">마감 시간</div>
                <div className="text-center">{hhmm(selectedOp.close_time)}</div>
              </div>
            </>
          ) : (
            <div className="text-center text-[14px] text-custom-black/60">
              표시할 영업 시간이 없습니다.
            </div>
          )}
        </div>
      </div>

      {items.map((item) => (
        <div
          key={item.to}
          className="flex flex-row items-center justify-between"
        >
          <div
            className="w-full bodyFont font-bold py-[20px] border-b-[1px] border-black/10 cursor-pointer"
            onClick={() => navigate(item.to)}
          >
            {item.label}
          </div>
          {reservation.length !== 0 && item.label === "운영 시간 변경" && (
            <div className="tagFont font-bold bg-main-pale border border-main-deep text-main-deep rounded-sm py-[8px] px-[16px]">
              변경 예약중
            </div>
          )}
        </div>
      ))}

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

export default ChangeOperationInfo;
