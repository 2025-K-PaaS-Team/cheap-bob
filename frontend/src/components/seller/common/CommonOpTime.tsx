import { daysOfWeek } from "@constant";
import type { OperationTimeType } from "@interface";
import { useMemo, useState } from "react";

interface OpProps {
  form: OperationTimeType[];
  setForm: (times: OperationTimeType[]) => void;
}

const CommonOpTime = ({ form, setForm }: OpProps) => {
  const [isBatch, setIsBatch] = useState(false);

  // 항상 0~6 정렬(스토어가 보장해도 표시용 정렬로 한 번 더)
  const sortedForm = useMemo(
    () => [...form].sort((a, b) => a.day_of_week - b.day_of_week),
    [form]
  );

  // 요일 토글: 삭제 금지, is_open_enabled만 토글
  const handleClickDays = (idx: number) => {
    const next = form.map((f) =>
      f.day_of_week === idx ? { ...f, is_open_enabled: !f.is_open_enabled } : f
    );
    setForm(next);
  };

  // helper: time string -> [hour, min]
  const parseTimeParts = (time?: string) => {
    if (!time) return ["", ""];
    const [h = "", m = ""] = time.split(":");
    return [h, m];
  };

  // clamp + format
  const clampAndFormat = (value: string, part: "hour" | "min") => {
    if (value === "") return "";
    const n = parseInt(value.replace(/\D/g, "").slice(-2), 10);
    if (isNaN(n)) return "";
    const clamped = Math.max(0, Math.min(part === "hour" ? 23 : 59, n));
    return String(clamped).padStart(2, "0");
  };

  // build "HH:MM:SS" (빈 값 허용)
  const buildTimeString = (hh: string, mm: string) =>
    hh === "" && mm === ""
      ? ""
      : `${hh.padStart(2, "0")}:${mm.padStart(2, "0")}:00`;

  // 배치 입력 상태
  const [batchOpen, setBatchOpen] = useState<[string, string]>(["", ""]);
  const [batchClose, setBatchClose] = useState<[string, string]>(["", ""]);

  // 배치 변경: 운영 요일(is_open_enabled)만 적용
  const handleBatchChange = (
    type: "open" | "close",
    part: "hour" | "min",
    rawValue: string
  ) => {
    const value = clampAndFormat(rawValue, part);

    if (type === "open") {
      const nextOpen: [string, string] = [...batchOpen] as any;
      nextOpen[part === "hour" ? 0 : 1] = value;
      setBatchOpen(nextOpen);

      const timeStr = buildTimeString(nextOpen[0], nextOpen[1]);
      const next = form.map((f) =>
        f.is_open_enabled ? { ...f, open_time: timeStr } : f
      );
      setForm(next);
    } else {
      const nextClose: [string, string] = [...batchClose] as any;
      nextClose[part === "hour" ? 0 : 1] = value;
      setBatchClose(nextClose);

      const timeStr = buildTimeString(nextClose[0], nextClose[1]);
      const next = form.map((f) =>
        f.is_open_enabled ? { ...f, close_time: timeStr } : f
      );
      setForm(next);
    }
  };

  // 일반 모드: 해당 요일만 변경
  const handleSingleChange = (
    dayIdx: number,
    type: "open" | "close",
    part: "hour" | "min",
    rawValue: string
  ) => {
    const value = clampAndFormat(rawValue, part);

    const next = form.map((f) => {
      if (f.day_of_week !== dayIdx) return f;

      const [oh, om] = parseTimeParts(f.open_time);
      const [ch, cm] = parseTimeParts(f.close_time);

      if (type === "open") {
        const hh = part === "hour" ? value : oh;
        const mm = part === "min" ? value : om;
        return { ...f, open_time: buildTimeString(hh, mm) };
      } else {
        const hh = part === "hour" ? value : ch;
        const mm = part === "min" ? value : cm;
        return { ...f, close_time: buildTimeString(hh, mm) };
      }
    });

    setForm(next);
  };

  return (
    <>
      {/* operation days */}
      <div className="flex flex-col gap-y-[10px] mt-[38px]">
        <div className="text-[14px] font-bold">운영 요일</div>
        <div className="text-[14px]">
          매장을 운영하는 날짜를 모두 선택해 주세요.
        </div>
        <div className="grid grid-cols-7">
          {daysOfWeek.map((day) => {
            const enabled = !!form.find(
              (f) => f.day_of_week === day.idx && f.is_open_enabled
            );
            return (
              <div
                key={day.idx}
                className={`text-[20px] h-[40px] w-[40px] flex justify-center items-center rounded-full cursor-pointer ${
                  enabled ? "bg-custom-white" : ""
                }`}
                onClick={() => handleClickDays(day.idx)}
                title={enabled ? "운영" : "휴무"}
              >
                {day.label}
              </div>
            );
          })}
        </div>
      </div>

      {/* operation time */}
      <div className="flex flex-col mt-[40px] gap-y-[10px]">
        <div className="text-[14px] font-bold">매장 운영 시간</div>
        <div className="text-[14px]">매장을 운영하는 시간을 입력해 주세요.</div>

        {/* batch checkbox */}
        <div className="flex flex-row gap-x-[22px]">
          <input
            type="checkbox"
            id="batchTime"
            checked={isBatch}
            onChange={() => setIsBatch((s) => !s)}
          />
          <span>시간 일괄 적용 (운영 요일만 적용)</span>
        </div>

        {isBatch ? (
          // 배치 모드
          <div className="flex flex-col gap-y-[20px] justify-center items-center">
            {/* open */}
            <span className="w-[70px] font-bold text-[14px] text-center">
              매장 오픈
            </span>
            <div className="flex flex-row gap-x-[10px] items-center justify-center text-[20px]">
              <input
                className="text-center bg-custom-white rounded-sm w-[50px] h-[44px]"
                value={batchOpen[0]}
                onChange={(e) =>
                  handleBatchChange("open", "hour", e.target.value)
                }
                inputMode="numeric"
                placeholder="hh"
              />
              <span>시</span>
              <input
                className="text-center bg-custom-white rounded-sm w-[50px] h-[44px]"
                value={batchOpen[1]}
                onChange={(e) =>
                  handleBatchChange("open", "min", e.target.value)
                }
                inputMode="numeric"
                placeholder="mm"
              />
              <span>분</span>
            </div>

            <hr className="border-0 h-[1px] bg-black my-[5px]" />

            {/* close */}
            <span className="w-[70px] font-bold">매장 마감</span>
            <div className="flex flex-row gap-x-[10px] items-center justify-center text-[20px]">
              <input
                className="text-center bg-custom-white rounded-sm w-[50px] h-[44px]"
                value={batchClose[0]}
                onChange={(e) =>
                  handleBatchChange("close", "hour", e.target.value)
                }
                inputMode="numeric"
                placeholder="hh"
              />
              <span>시</span>
              <input
                className="text-center bg-custom-white rounded-sm w-[50px] h-[44px]"
                value={batchClose[1]}
                onChange={(e) =>
                  handleBatchChange("close", "min", e.target.value)
                }
                inputMode="numeric"
                placeholder="mm"
              />
              <span>분</span>
            </div>
          </div>
        ) : (
          // 일반 모드
          <div className="flex flex-col items-center overflow-y-auto h-[220px] w-full">
            {sortedForm.map((day) => {
              const [openHour, openMin] = parseTimeParts(day.open_time);
              const [closeHour, closeMin] = parseTimeParts(day.close_time);
              const disabled = !day.is_open_enabled;

              return (
                <div
                  key={day.day_of_week}
                  className="grid grid-cols-8 w-full items-center"
                >
                  <div className="font-bold text-[14px] h-[40px] flex items-center justify-center">
                    {daysOfWeek[day.day_of_week].label}
                  </div>

                  {/* Open time */}
                  <div className="col-span-3 text-center flex flex-row gap-x-[5px] justify-center">
                    <input
                      className="w-[36px] text-center bg-custom-white rounded disabled:opacity-50"
                      value={openHour}
                      onChange={(e) =>
                        handleSingleChange(
                          day.day_of_week,
                          "open",
                          "hour",
                          e.target.value
                        )
                      }
                      inputMode="numeric"
                      placeholder="hh"
                      disabled={disabled}
                    />
                    <div>시</div>
                    <input
                      className="w-[36px] text-center bg-custom-white rounded disabled:opacity-50"
                      value={openMin}
                      onChange={(e) =>
                        handleSingleChange(
                          day.day_of_week,
                          "open",
                          "min",
                          e.target.value
                        )
                      }
                      inputMode="numeric"
                      placeholder="mm"
                      disabled={disabled}
                    />
                    <div>분</div>
                  </div>

                  <div className="text-center font-bold">~</div>

                  {/* Close time */}
                  <div className="col-span-3 text-center flex flex-row gap-x-[5px] justify-center">
                    <input
                      className="w-[36px] text-center bg-custom-white rounded disabled:opacity-50"
                      value={closeHour}
                      onChange={(e) =>
                        handleSingleChange(
                          day.day_of_week,
                          "close",
                          "hour",
                          e.target.value
                        )
                      }
                      inputMode="numeric"
                      placeholder="hh"
                      disabled={disabled}
                    />
                    <div>시</div>
                    <input
                      className="w-[36px] text-center bg-custom-white rounded disabled:opacity-50"
                      value={closeMin}
                      onChange={(e) =>
                        handleSingleChange(
                          day.day_of_week,
                          "close",
                          "min",
                          e.target.value
                        )
                      }
                      inputMode="numeric"
                      placeholder="mm"
                      disabled={disabled}
                    />
                    <div>분</div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </>
  );
};

export default CommonOpTime;
