import type { OperationTimeType } from "@interface";
import { useEffect, useState } from "react";

interface OpProps {
  form: OperationTimeType[];
  setForm: (times: OperationTimeType[]) => void;
}
const CommonOpTime = ({ form, setForm }: OpProps) => {
  const [isBatch, setIsBatch] = useState(false);
  const [opDay, setOpDay] = useState<number[]>(form.map((f) => f.day_of_week));
  const daysOfWeek = [
    { label: "월", idx: 0 },
    { label: "화", idx: 1 },
    { label: "수", idx: 2 },
    { label: "목", idx: 3 },
    { label: "금", idx: 4 },
    { label: "토", idx: 5 },
    { label: "일", idx: 6 },
  ];

  useEffect(() => {
    // opDay 바뀔 때마다 form을 새로 계산
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
    setForm(newForm);
  }, [opDay]);

  const handleClickDays = (idx: number) => {
    setOpDay((prev) =>
      prev.includes(idx)
        ? prev.filter((day) => day !== idx)
        : [...prev, idx].sort((a, b) => a - b)
    );
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
          {daysOfWeek.map((day) => (
            <div
              className={`text-[20px] h-[40px] w-[40px] aspect-square text-center flex justify-center items-center rounded-full ${
                opDay.includes(day.idx) ? "bg-[#d9d9d9]" : ""
              }`}
              key={day.idx}
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
            onChange={() => setIsBatch(!isBatch)}
          />
          <span>시간 일괄 적용</span>
        </div>

        {/* list header*/}
        <div className="grid grid-cols-8">
          <div />
          <div className="col-span-3 text-center">매장 오픈</div>
          <div />
          <div className="col-span-3 text-center">매장 마감</div>
        </div>

        {/* list content */}
        <div className="flex flex-col items-center overflow-y-auto h-[220px]">
          {form
            .sort((a, b) => a.day_of_week - b.day_of_week)
            .map((day) => {
              const openHour = day.open_time.split(":")[0] || "00";
              const openMin = day.open_time.split(":")[1] || "00";
              const closeHour = day.close_time.split(":")[0] || "23";
              const closeMin = day.close_time.split(":")[1] || "59";

              const handleTimeChange = (
                type: "open" | "close",
                part: "hour" | "min",
                value: string,
                dayOfWeek: number
              ) => {
                let hh = value;
                let mm = value;

                // 현재 day의 기존 시간 가져오기
                const targetDay = form.find(
                  (f) => f.day_of_week === dayOfWeek
                )!;
                const [curOpenH = "00", curOpenM = "00"] = targetDay.open_time
                  ? targetDay.open_time.split(":")
                  : ["00", "00"];
                const [curCloseH = "23", curCloseM = "59"] =
                  targetDay.close_time
                    ? targetDay.close_time.split(":")
                    : ["23", "59"];

                if (type === "open") {
                  hh =
                    part === "hour"
                      ? value.padStart(2, "0")
                      : curOpenH.padStart(2, "0");
                  mm =
                    part === "min"
                      ? value.padStart(2, "0")
                      : curOpenM.padStart(2, "0");
                } else {
                  hh =
                    part === "hour"
                      ? value.padStart(2, "0")
                      : curCloseH.padStart(2, "0");
                  mm =
                    part === "min"
                      ? value.padStart(2, "0")
                      : curCloseM.padStart(2, "0");
                }

                if (hh.length > 2) hh = hh.slice(-2);
                if (mm.length > 2) mm = mm.slice(-2);

                let newForm = form.map((f) =>
                  f.day_of_week === dayOfWeek
                    ? { ...f, [type + "_time"]: `${hh}:${mm}:00` }
                    : f
                );

                // batch 적용
                if (isBatch) {
                  newForm = newForm.map((f) =>
                    opDay.includes(f.day_of_week)
                      ? { ...f, [type + "_time"]: `${hh}:${mm}:00` }
                      : f
                  );
                }

                setForm(newForm);
              };

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
                        handleTimeChange(
                          "open",
                          "hour",
                          e.target.value,
                          day.day_of_week
                        )
                      }
                    />
                    <div>시</div>
                    <input
                      className="w-[36px] text-center bg-[#d9d9d9] rounded"
                      value={openMin}
                      onChange={(e) =>
                        handleTimeChange(
                          "open",
                          "hour",
                          e.target.value,
                          day.day_of_week
                        )
                      }
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
                        handleTimeChange(
                          "open",
                          "hour",
                          e.target.value,
                          day.day_of_week
                        )
                      }
                    />
                    <div>시</div>
                    <input
                      className="w-[36px] text-center bg-[#d9d9d9] rounded"
                      value={closeMin}
                      onChange={(e) =>
                        handleTimeChange(
                          "open",
                          "hour",
                          e.target.value,
                          day.day_of_week
                        )
                      }
                    />
                    <div>분</div>
                  </div>
                </div>
              );
            })}
        </div>
      </div>
    </>
  );
};

export default CommonOpTime;
