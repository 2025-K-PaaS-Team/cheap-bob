import type { OperationTimeType } from "@interface";
import { useEffect, useState } from "react";

interface OpProps {
  form: OperationTimeType[];
  setForm: (times: OperationTimeType[]) => void;
}

const CommonOpTime = ({ form, setForm }: OpProps) => {
  const [isBatch, setIsBatch] = useState(false);
  const [opDay, setOpDay] = useState<number[]>(() =>
    [...form.map((f) => f.day_of_week)].sort((a, b) => a - b)
  );

  const daysOfWeek = [
    { label: "월", idx: 0 },
    { label: "화", idx: 1 },
    { label: "수", idx: 2 },
    { label: "목", idx: 3 },
    { label: "금", idx: 4 },
    { label: "토", idx: 5 },
    { label: "일", idx: 6 },
  ];

  // opDay가 바뀌면 form의 날짜 라인업을 동일하게 유지
  useEffect(() => {
    const newForm = opDay.map((day) => {
      const exist = form.find((f) => f.day_of_week === day);
      return (
        exist || {
          day_of_week: day,
          open_time: "",
          pickup_start_time: "",
          pickup_end_time: "",
          close_time: "",
          is_open_enabled: true,
        }
      );
    });

    const formDays = [...form.map((f) => f.day_of_week)].sort((a, b) => a - b);
    const newDays = [...newForm.map((f) => f.day_of_week)].sort(
      (a, b) => a - b
    );

    const same =
      formDays.length === newDays.length &&
      formDays.every((d, i) => d === newDays[i]);

    if (!same) setForm(newForm);
  }, [opDay, setForm, form]);

  // 부모 form이 바뀌면 opDay 동기화
  useEffect(() => {
    const days = [...form.map((f) => f.day_of_week)].sort((a, b) => a - b);
    const same =
      days.length === opDay.length && days.every((d, i) => d === opDay[i]);
    if (!same) setOpDay(days);
  }, [form]);

  const handleClickDays = (idx: number) => {
    setOpDay((prev) =>
      prev.includes(idx)
        ? prev.filter((day) => day !== idx)
        : [...prev, idx].sort((a, b) => a - b)
    );
  };

  // helper: time string -> [hour, min]
  const parseTimeParts = (time?: string) => {
    if (!time) return ["", ""];
    const parts = time.split(":");
    return [parts[0] ?? "", parts[1] ?? ""];
  };

  // clamp + format
  const clampAndFormat = (value: string, part: "hour" | "min") => {
    if (value === "") return "";
    const n = parseInt(value, 10);
    if (isNaN(n)) return "";
    const clamped = Math.max(0, Math.min(part === "hour" ? 23 : 59, n));
    return String(clamped).padStart(2, "0");
  };

  // build time string
  const buildTimeString = (hh: string, mm: string) =>
    hh === "" && mm === ""
      ? ""
      : `${hh.padStart(2, "0")}:${mm.padStart(2, "0")}:00`;

  // 배치 입력 상태
  const [batchOpen, setBatchOpen] = useState(["", ""]);
  const [batchClose, setBatchClose] = useState(["", ""]);

  // 배치 변경
  const handleBatchChange = (
    type: "open" | "close",
    part: "hour" | "min",
    rawValue: string
  ) => {
    let value = rawValue.replace(/\D/g, "");
    if (value.length > 2) value = value.slice(-2);
    value = clampAndFormat(value, part);

    if (type === "open") {
      const newOpen = [...batchOpen];
      newOpen[part === "hour" ? 0 : 1] = value;
      setBatchOpen(newOpen);

      const timeStr = buildTimeString(newOpen[0], newOpen[1]);
      const next = form.map((f) =>
        opDay.includes(f.day_of_week) ? { ...f, open_time: timeStr } : f
      );
      setForm(next);
    } else {
      const newClose = [...batchClose];
      newClose[part === "hour" ? 0 : 1] = value;
      setBatchClose(newClose);

      const timeStr = buildTimeString(newClose[0], newClose[1]);
      const next = form.map((f) =>
        opDay.includes(f.day_of_week) ? { ...f, close_time: timeStr } : f
      );
      setForm(next);
    }
  };

  // ★ 일반 모드: 해당 요일만 변경
  const handleSingleChange = (
    dayIdx: number,
    type: "open" | "close",
    part: "hour" | "min",
    rawValue: string
  ) => {
    let value = rawValue.replace(/\D/g, "");
    if (value.length > 2) value = value.slice(-2);
    value = clampAndFormat(value, part);

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

  const sortedForm = [...form].sort((a, b) => a.day_of_week - b.day_of_week);

  return (
    <>
      {/* operation days */}
      <div className="flex flex-col gap-y-[10px] mt-[38px]">
        <div className="text-[14px] font-bold">운영 요일</div>
        <div className="text-[14px]">
          매장을 운영하는 날짜를 모두 선택해 주세요.
        </div>
        <div className="grid grid-cols-7">
          {daysOfWeek.map((day) => (
            <div
              key={day.idx}
              className={`text-[20px] h-[40px] w-[40px] flex justify-center items-center rounded-full cursor-pointer ${
                opDay.includes(day.idx) ? "bg-[#d9d9d9]" : ""
              }`}
              onClick={() => handleClickDays(day.idx)}
            >
              {day.label}
            </div>
          ))}
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
          <span>시간 일괄 적용</span>
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
                className="text-center bg-[#d9d9d9] rounded-[8px] w-[50px] h-[44px]"
                value={batchOpen[0]}
                onChange={(e) =>
                  handleBatchChange("open", "hour", e.target.value)
                }
                inputMode="numeric"
                placeholder="hh"
              />
              <span>시</span>
              <input
                className="text-center bg-[#d9d9d9] rounded-[8px] w-[50px] h-[44px]"
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
            <div className="flex flex-row gap-x={[10].toString()} items-center justify-center text-[20px]">
              <input
                className="text-center bg-[#d9d9d9] rounded-[8px] w-[50px] h-[44px]"
                value={batchClose[0]}
                onChange={(e) =>
                  handleBatchChange("close", "hour", e.target.value)
                }
                inputMode="numeric"
                placeholder="hh"
              />
              <span>시</span>
              <input
                className="text-center bg-[#d9d9d9] rounded-[8px] w-[50px] h-[44px]"
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
          // 일반 모드 (★ 단일 요일만 변경)
          <div className="flex flex-col items-center overflow-y-auto h-[220px] w-full">
            {sortedForm.map((day) => {
              const [openHour, openMin] = parseTimeParts(day.open_time);
              const [closeHour, closeMin] = parseTimeParts(day.close_time);

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
                      className="w-[36px] text-center bg-[#d9d9d9] rounded"
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
                    />
                    <div>시</div>
                    <input
                      className="w-[36px] text-center bg-[#d9d9d9] rounded"
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
                    />
                    <div>분</div>
                  </div>

                  <div className="text-center font-bold">~</div>

                  {/* Close time */}
                  <div className="col-span-3 text-center flex flex-row gap-x-[5px] justify-center">
                    <input
                      className="w-[36px] text-center bg-[#d9d9d9] rounded"
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
                    />
                    <div>시</div>
                    <input
                      className="w-[36px] text-center bg-[#d9d9d9] rounded"
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
