import { daysOfWeek } from "@constant";
import type { OperationTimeType } from "@interface";
import { useEffect, useMemo, useRef, useState } from "react";

interface OpProps {
  originForm: OperationTimeType[];
  form: OperationTimeType[];
  setForm: (times: OperationTimeType[]) => void;
}

const CommonOpTime = ({ originForm, form, setForm }: OpProps) => {
  const [isBatch, setIsBatch] = useState(false);

  const initialFormRef = useRef<OperationTimeType[] | null>(null);
  useEffect(() => {
    if (!initialFormRef.current && originForm?.length) {
      initialFormRef.current = JSON.parse(JSON.stringify(originForm));
    }
  }, [originForm]);

  // --- 표시용 정렬 ---
  const sortedForm = useMemo(
    () => [...form].sort((a, b) => a.day_of_week - b.day_of_week),
    [form]
  );

  const parseTimeParts = (time?: string) => {
    if (!time) return ["", ""];
    const [h = "", m = ""] = time.split(":");
    return [h, m];
  };
  const formatWithColon = (val: string) => {
    const numbers = (val || "").replace(/\D/g, "").slice(0, 4);
    return numbers.length <= 2
      ? numbers
      : numbers.slice(0, 2) + ":" + numbers.slice(2);
  };
  const clamp = (n: number, min: number, max: number) =>
    Math.max(min, Math.min(max, n));

  const makeTimeOrBlank = (hhRaw: string, mmRaw: string) => {
    const hStr = hhRaw.replace(/\D/g, "").slice(0, 2);
    const mStr = mmRaw.replace(/\D/g, "").slice(0, 2);
    if (!hStr && !mStr) return "";
    const h = clamp(parseInt(hStr || "0", 10) || 0, 0, 23);
    const m = clamp(parseInt(mStr || "0", 10) || 0, 0, 59);
    return `${String(h).padStart(2, "0")}:${String(m).padStart(2, "0")}:00`;
  };

  const handleClickDays = (idx: number) => {
    const next = form.map((f) =>
      f.day_of_week === idx ? { ...f, is_open_enabled: !f.is_open_enabled } : f
    );
    setForm(next);
  };

  const [rawTimeMap, setRawTimeMap] = useState<
    Record<number, { open: string; close: string }>
  >(() => {
    const init: Record<number, { open: string; close: string }> = {};
    form.forEach((f) => {
      const [oh, om] = parseTimeParts(f.open_time);
      const [ch, cm] = parseTimeParts(f.close_time);
      init[f.day_of_week] = {
        open: (oh || "") + (om || ""),
        close: (ch || "") + (cm || ""),
      };
    });
    return init;
  });

  useEffect(() => {
    console.log(form);
    const next: Record<number, { open: string; close: string }> = {};
    form.forEach((f) => {
      const [oh, om] = parseTimeParts(f.open_time);
      const [ch, cm] = parseTimeParts(f.close_time);
      next[f.day_of_week] = {
        open: (oh || "") + (om || ""),
        close: (ch || "") + (cm || ""),
      };
    });
    setRawTimeMap(next);
  }, [form]);

  const commitTime = (
    dayIdx: number,
    which: "open" | "close",
    hhmmRaw: string
  ) => {
    const raw = (hhmmRaw || "").replace(/\D/g, "").slice(0, 4);
    if (raw.length === 0) {
      setForm(
        form.map((f) =>
          f.day_of_week === dayIdx
            ? { ...f, [which === "open" ? "open_time" : "close_time"]: "" }
            : f
        )
      );
      return;
    }
    let hh = raw.slice(0, 2);
    let mm = raw.slice(2, 4) || "";
    const timeStr = makeTimeOrBlank(hh, mm);
    setForm(
      form.map((f) =>
        f.day_of_week === dayIdx
          ? { ...f, [which === "open" ? "open_time" : "close_time"]: timeStr }
          : f
      )
    );
  };

  const handleRawChange = (
    dayIdx: number,
    which: "open" | "close",
    e: React.ChangeEvent<HTMLInputElement>
  ) => {
    const onlyNum = e.target.value.replace(/\D/g, "").slice(0, 4);
    setRawTimeMap((prev) => ({
      ...prev,
      [dayIdx]: { ...prev[dayIdx], [which]: onlyNum },
    }));
    if (onlyNum.length === 4) commitTime(dayIdx, which, onlyNum);
  };

  const handleBlur = (dayIdx: number, which: "open" | "close") => {
    const buf = rawTimeMap[dayIdx]?.[which] ?? "";
    commitTime(dayIdx, which, buf);
  };

  const handleKeyDown = (
    _dayIdx: number,
    _which: "open" | "close",
    e: React.KeyboardEvent<HTMLInputElement>
  ) => {
    if (e.key === "Enter") e.currentTarget.blur();
  };

  const [batchOpen, setBatchOpen] = useState<[string, string]>(["", ""]);
  const [batchClose, setBatchClose] = useState<[string, string]>(["", ""]);

  const handleBatchRaw = (
    type: "open" | "close",
    part: "hour" | "min",
    rawValue: string
  ) => {
    const v = rawValue.replace(/\D/g, "").slice(0, 2);

    if (type === "open") {
      const next: [string, string] = [...batchOpen];
      next[part === "hour" ? 0 : 1] = v;
      setBatchOpen(next);

      const openStr = makeTimeOrBlank(next[0], next[1]);
      setForm(
        form.map((f) => (f.is_open_enabled ? { ...f, open_time: openStr } : f))
      );
    } else {
      const next: [string, string] = [...batchClose];
      next[part === "hour" ? 0 : 1] = v;
      setBatchClose(next);

      const closeStr = makeTimeOrBlank(next[0], next[1]);
      setForm(
        form.map((f) =>
          f.is_open_enabled ? { ...f, close_time: closeStr } : f
        )
      );
    }
  };

  const handleResetTimesOnly = () => {
    const base = initialFormRef.current ?? form;
    const next = form.map((f) => {
      const init = base.find((x) => x.day_of_week === f.day_of_week);
      return {
        ...f,
        open_time: init?.open_time ?? "",
        close_time: init?.close_time ?? "",
      };
    });
    setForm(next);
    setBatchOpen(["", ""]);
    setBatchClose(["", ""]);
  };

  const handleResetDaysOnly = () => {
    const base = initialFormRef.current ?? form;
    const next = form.map((f) => {
      const init = base.find((x) => x.day_of_week === f.day_of_week);
      return { ...f, is_open_enabled: init?.is_open_enabled ?? false };
    });
    setForm(next);
  };

  return (
    <div className="flex flex-col w-full gap-y-[20px]">
      {/* 영업 요일 */}
      <div className="flex flex-col gap-y-[10px]">
        <h3>영업 요일</h3>
        <div className="bodyFont">
          매장을 운영하는 날짜를 모두 선택해 주세요.
        </div>

        <div className="grid grid-cols-7">
          {daysOfWeek.map((day) => {
            const enabled = !!form.find(
              (f) => f.day_of_week === day.idx && f.is_open_enabled
            );
            return (
              <div className="flex justify-center" key={day.idx}>
                <div
                  className={`hintFont h-[36px] w-[36px] flex justify-center items-center rounded-full cursor-pointer ${
                    enabled
                      ? "bg-main-deep text-white font-bold"
                      : "bg-custom-white"
                  }`}
                  onClick={() => handleClickDays(day.idx)}
                  title={enabled ? "운영" : "휴무"}
                >
                  {day.label}
                </div>
              </div>
            );
          })}
        </div>

        <div className="flex justify-end gap-3 btnFont">
          <button
            type="button"
            className="text-main-deep"
            onClick={handleResetDaysOnly}
          >
            초기화
          </button>
        </div>
      </div>

      <hr className="border-0 h-[1px] w-full bg-[#E7E7E7]" />

      {/* 영업 시간 */}
      <div className="flex flex-col gap-y-[10px]">
        <h3>영업 시간</h3>
        <div className="bodyFont">매장이 영업하는 시간을 설정해 주세요.</div>

        {/* 배치 체크박스 */}
        <div className="flex flex-row gap-x-[10px]">
          <input
            type="checkbox"
            id="batchTime"
            checked={isBatch}
            onChange={() => setIsBatch((s) => !s)}
          />
          <span className="bodyFont">시간 일괄 적용</span>
        </div>

        {isBatch ? (
          // 배치 모드 (입력 즉시 반영)
          <div className="flex flex-col gap-y-[10px] justify-center items-center">
            <span className="text-custom-black font-bold">매장 오픈</span>
            <div className="flex flex-row gap-x-[10px] items-center justify-center text-[20px]">
              <input
                className="text-center bg-[#E7E7E7] rounded-sm w-[50px] h-[44px]"
                value={batchOpen[0]}
                onChange={(e) => handleBatchRaw("open", "hour", e.target.value)}
                inputMode="numeric"
                placeholder="hh"
              />
              <span>시</span>
              <input
                className="text-center bg-[#E7E7E7] rounded-sm w-[50px] h-[44px]"
                value={batchOpen[1]}
                onChange={(e) => handleBatchRaw("open", "min", e.target.value)}
                inputMode="numeric"
                placeholder="mm"
              />
              <span>분</span>
            </div>

            <hr className="border-0 h-[1px] w-full bg-[#E7E7E7]" />

            <span className="text-custom-black font-bold">매장 마감</span>
            <div className="flex flex-row gap-x-[10px] items-center justify-center text-[20px]">
              <input
                className="text-center bg-[#E7E7E7] rounded-sm w-[50px] h-[44px]"
                value={batchClose[0]}
                onChange={(e) =>
                  handleBatchRaw("close", "hour", e.target.value)
                }
                inputMode="numeric"
                placeholder="hh"
              />
              <span>시</span>
              <input
                className="text-center bg-[#E7E7E7] rounded-sm w-[50px] h-[44px]"
                value={batchClose[1]}
                onChange={(e) => handleBatchRaw("close", "min", e.target.value)}
                inputMode="numeric"
                placeholder="mm"
              />
              <span>분</span>
            </div>
          </div>
        ) : (
          // 일반 모드
          <div className="flex flex-col">
            <div className="grid grid-cols-8 w-full items-center">
              <div className="col-span-2"></div>
              <div className="font-bold col-span-2">매장 오픈</div>
              <div className="col-span-2"></div>
              <div className="font-bold col-span-2">매장 마감</div>
            </div>

            <div className="flex flex-col items-center w-full">
              {sortedForm
                .filter((day) => day.is_open_enabled)
                .map((day) => {
                  const disabled = !day.is_open_enabled;
                  return (
                    <div
                      className="flex flex-col w-full hintFont"
                      key={day.day_of_week}
                    >
                      <div className="grid grid-cols-8 w-full items-center">
                        <div className="font-bold text-[14px] h-[40px] flex items-center justify-center">
                          {daysOfWeek[day.day_of_week].label}
                        </div>

                        {/* Open time */}
                        <div className="col-span-3 text-center flex flex-row justify-center border-b border-[#393939] pb-1">
                          <input
                            className="w-[50px] text-center"
                            value={formatWithColon(
                              rawTimeMap[day.day_of_week]?.open || ""
                            )}
                            onChange={(e) =>
                              handleRawChange(day.day_of_week, "open", e)
                            }
                            onBlur={() => handleBlur(day.day_of_week, "open")}
                            onKeyDown={(e) =>
                              handleKeyDown(day.day_of_week, "open", e)
                            }
                            inputMode="numeric"
                            placeholder="hhmm"
                            disabled={disabled}
                          />
                        </div>

                        <div className="text-center font-bold">~</div>

                        {/* Close time */}
                        <div className="col-span-3 text-center flex flex-row justify-center border-b border-[#393939] pb-1">
                          <input
                            className="w-[50px] text-center"
                            value={formatWithColon(
                              rawTimeMap[day.day_of_week]?.close || ""
                            )}
                            onChange={(e) =>
                              handleRawChange(day.day_of_week, "close", e)
                            }
                            onBlur={() => handleBlur(day.day_of_week, "close")}
                            onKeyDown={(e) =>
                              handleKeyDown(day.day_of_week, "close", e)
                            }
                            inputMode="numeric"
                            placeholder="hhmm"
                            disabled={disabled}
                          />
                        </div>
                      </div>
                    </div>
                  );
                })}
            </div>
          </div>
        )}

        {/* 시간만 초기화 */}
        <div className="flex justify-end btnFont">
          <button
            type="button"
            className="text-main-deep"
            onClick={handleResetTimesOnly}
          >
            초기화
          </button>
        </div>
      </div>
    </div>
  );
};

export default CommonOpTime;
