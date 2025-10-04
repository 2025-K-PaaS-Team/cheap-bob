import { CommonModal } from "@components/common";
import { idxToDow } from "@constant";
import type { StoreOperationType } from "@interface";
import { GetStoreOperation } from "@services";
import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router";

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
    { label: "운영 시간 변경", to: "/s/change/operation/op-time" },
    { label: "픽업 시간 변경", to: "/s/change/operation/pu-time" },
  ];

  const [op, setOp] = useState<StoreOperationType>([]);
  const [selectedDow, setSelectedDow] = useState<number | null>(null);
  const [showModal, setShowModal] = useState(false);
  const [modalMsg, setModalMsg] = useState("");
  const [loading, setLoading] = useState(true);

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
      setLoading(false);
    }
  };

  useEffect(() => {
    handleGetStoreOperation();
  }, []);

  if (loading) return <div className="mx-[35px]">로딩중...</div>;

  return (
    <div className="mx-[35px]">
      <div className="flex flex-col gap-y-[9px]">
        <div className="text-[16px]">현재 영업 시간</div>

        {/* 영업 요일: 활성 요일만 */}
        <div className="text-[14px] flex flex-row">
          <div className="flex items-center justify-center mr-[40px]">
            영업 요일
          </div>
          <div className="flex flex-row gap-x-[6px]">
            {activeDays.length === 0 ? (
              <div className="text-[13px] text-black/50">
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
                    className={`w-[32px] h-[32px] rounded-full flex items-center justify-center
                      ${
                        isSelected
                          ? "bg-black text-white"
                          : "bg-[#D9D9D9] text-black"
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
        </div>

        {/* 선택된 요일의 시간 */}
        <div className="bg-[#D9D9D9] rounded-[8px] my-[8px] flex flex-col py-[15px] px-[23px] space-y-[10px]">
          {selectedOp ? (
            <>
              <div className="grid grid-cols-3 items-center">
                <div className="text-[14px]">오픈 시간</div>
                <div className="text-[20px] col-span-2 text-center">
                  {hhmm(selectedOp.open_time)}
                </div>
              </div>
              <div className="grid grid-cols-3 items-center">
                <div className="text-[14px]">픽업 확정 시간</div>
                <div className="text-[20px] col-span-2 text-center">
                  {hhmm(selectedOp.pickup_start_time)}
                </div>
              </div>
              <div className="grid grid-cols-3 items-center">
                <div className="text-[14px]">픽업 마감 시간</div>
                <div className="text-[20px] col-span-2 text-center">
                  {hhmm(selectedOp.pickup_end_time)}
                </div>
              </div>
              <div className="grid grid-cols-3 items-center">
                <div className="text-[14px]">마감 시간</div>
                <div className="text-[20px] col-span-2 text-center">
                  {hhmm(selectedOp.close_time)}
                </div>
              </div>
            </>
          ) : (
            <div className="text-center text-[14px] text-black/60">
              표시할 영업 시간이 없습니다.
            </div>
          )}
        </div>
      </div>

      {items.map((item) => (
        <div key={item.to}>
          <div
            className="text-[16px] py-[20px] border-b-[1px] border-black/10 cursor-pointer"
            onClick={() => navigate(item.to)}
          >
            {item.label}
          </div>
        </div>
      ))}

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

export default ChangeOperationInfo;
