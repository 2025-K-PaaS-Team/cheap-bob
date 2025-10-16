import { idxToDow } from "@constant";
import type { Offset, OperationTimeType } from "@interface";
import { useEffect, useMemo } from "react";

interface PuTimeProps {
  form: OperationTimeType[];
  setForm: (times: OperationTimeType[]) => void;
  pickupStartOffset: Offset;
  setPickupStartOffset: (hour: number, min: number) => void;
  pickupDiscardOffset: Offset;
  setPickupDiscardOffset: (hour: number, min: number) => void;
}

const pad2 = (n: number) => String(n).padStart(2, "0");
const toHM = (t?: string) => {
  const [h = "0", m = "0"] = (t || "").split(":");
  return { h: Number(h) || 0, m: Number(m) || 0 };
};
const minusOffset = (h: number, m: number, oh: number, om: number) => {
  const base = h * 60 + m;
  const off = (oh * 60 + om) % 1440;
  const x = (((base - off) % 1440) + 1440) % 1440;
  return { h: Math.floor(x / 60), m: x % 60 };
};
const clampNum = (raw: string, max: number) => {
  const v = raw.replace(/\D/g, "");
  if (!v) return 0;
  const n = Math.min(max, Math.max(0, parseInt(v.slice(-2), 10) || 0));
  return n;
};

const CommonPuTime = ({
  form,
  setForm,
  pickupStartOffset,
  setPickupStartOffset,
  pickupDiscardOffset,
  setPickupDiscardOffset,
}: PuTimeProps) => {
  // 첫 운영일(비활성 제외) — 표기 기준
  const firstOpenDay = useMemo(() => {
    const open = form.filter((f) => f.is_open_enabled !== false);
    if (!open.length) return undefined;
    const minIdx = Math.min(...open.map((f) => f.day_of_week));
    return form.find((f) => f.day_of_week === minIdx);
  }, [form]);
  const baseLabel = firstOpenDay
    ? idxToDow[firstOpenDay.day_of_week]
    : "운영일";

  // 오프셋/close_time 변경 시 계산값 반영 (무한루프 방지: 실제 변경시에만 setForm)
  useEffect(() => {
    let changed = false;

    const next = form.map((f) => {
      if (!f.close_time) return f;

      const { h: ch, m: cm } = toHM(f.close_time);

      const s = minusOffset(
        ch,
        cm,
        pickupStartOffset.hour,
        pickupStartOffset.min
      );
      const d = minusOffset(
        ch,
        cm,
        pickupDiscardOffset.hour,
        pickupDiscardOffset.min
      );

      const startStr = `${pad2(s.h)}:${pad2(s.m)}:00`;
      const discardStr = `${pad2(d.h)}:${pad2(d.m)}:00`;

      if (
        f.pickup_start_time !== startStr ||
        (f.pickup_end_time || "") !== discardStr
      ) {
        changed = true;
        return {
          ...f,
          pickup_start_time: startStr,
          pickup_end_time: discardStr,
        };
      }
      return f;
    });

    if (changed) setForm(next);
  }, [form, setForm, pickupStartOffset, pickupDiscardOffset]);

  // 표시용 (첫 운영일 기준)
  const startDisplay = firstOpenDay?.pickup_start_time || "00:00:00";
  const [sHH = "00", sMM = "00"] = startDisplay.split(":");
  const discardDisplay = firstOpenDay?.pickup_end_time || "00:00:00";
  const [dHH = "00", dMM = "00"] = discardDisplay.split(":");

  return (
    <>
      {/* 픽업 시작 기준 (전부터) */}
      <div className="text-[14px] font-bold">픽업 시작</div>
      <div className="text-[14px]">
        마감 세일을 시작할 시간을 입력해 주세요.
      </div>
      <div className="text-center w-full justify-center">
        <div className="flex flex-row text-[20px] justify-center items-center gap-x-[10px]">
          <input
            className="bg-custom-white rounded-sm w-[50px] h-[44px] text-center"
            value={pickupStartOffset.hour}
            onChange={(e) =>
              setPickupStartOffset(
                clampNum(e.target.value, 23),
                pickupStartOffset.min
              )
            }
            inputMode="numeric"
            placeholder="hh"
          />
          <div>시</div>
          <input
            className="bg-custom-white rounded-sm w-[50px] h-[44px] text-center"
            value={pickupStartOffset.min}
            onChange={(e) =>
              setPickupStartOffset(
                pickupStartOffset.hour,
                clampNum(e.target.value, 59)
              )
            }
            inputMode="numeric"
            placeholder="mm"
          />
          <div>분 전부터</div>
        </div>
        <div className="text-[14px] mt-[10px]">
          손님들이 {sHH}시 {sMM}분부터 매장에 방문하여 <br />
          패키지를 픽업할 수 있습니다.
        </div>
      </div>

      {/* 픽업 마감(폐기) 기준 (전부터 / 이후 폐기) */}
      <div className="text-[14px] font-bold mt-[40px]">픽업 마감 시간</div>
      <div className="text-[14px]">픽업을 마감할 시간을 입력해 주세요.</div>
      <div className="text-center w-full justify-center">
        <div className="flex flex-row text-[20px] justify-center items-center gap-x-[10px]">
          <input
            className="bg-custom-white rounded-sm w-[50px] h-[44px] text-center"
            value={pickupDiscardOffset.hour}
            onChange={(e) =>
              setPickupDiscardOffset(
                clampNum(e.target.value, 23),
                pickupDiscardOffset.min
              )
            }
            inputMode="numeric"
            placeholder="hh"
          />
          <div>시</div>
          <input
            className="bg-custom-white rounded-sm w-[50px] h-[44px] text-center"
            value={pickupDiscardOffset.min}
            onChange={(e) =>
              setPickupDiscardOffset(
                pickupDiscardOffset.hour,
                clampNum(e.target.value, 59)
              )
            }
            inputMode="numeric"
            placeholder="mm"
          />
          <div>분 전부터</div>
        </div>
        <div className="text-[14px] mt-[10px]">
          {dHH}시 {dMM}분까지 픽업되지 않은 패키지는 폐기합니다.
        </div>
      </div>
    </>
  );
};

export default CommonPuTime;
