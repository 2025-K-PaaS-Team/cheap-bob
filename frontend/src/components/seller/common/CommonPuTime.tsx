import type { Offset, OperationTimeType } from "@interface";
import { clampNum, minusOffset, pad2, toHM } from "@utils";
import { useEffect, useMemo, useRef } from "react";

interface PuTimeProps {
  form: OperationTimeType[];
  setForm: (times: OperationTimeType[]) => void;
  pickupStartOffset: Offset;
  setPickupStartOffset: (hour: number, min: number) => void;
  pickupDiscardOffset: Offset;
  setPickupDiscardOffset: (hour: number, min: number) => void;
}

const CommonPuTime = ({
  form,
  setForm,
  pickupStartOffset,
  setPickupStartOffset,
  pickupDiscardOffset,
  setPickupDiscardOffset,
}: PuTimeProps) => {
  const initialOffsetsRef = useRef<{
    start: Offset;
    discard: Offset;
  } | null>(null);

  useEffect(() => {
    if (!initialOffsetsRef.current) {
      initialOffsetsRef.current = {
        start: { hour: pickupStartOffset.hour, min: pickupStartOffset.min },
        discard: {
          hour: pickupDiscardOffset.hour,
          min: pickupDiscardOffset.min,
        },
      };
    }
  }, [pickupStartOffset, pickupDiscardOffset]);

  const firstOpenDay = useMemo(() => {
    const open = form.filter((f) => f.is_open_enabled !== false);
    if (!open.length) return undefined;
    const minIdx = Math.min(...open.map((f) => f.day_of_week));
    return form.find((f) => f.day_of_week === minIdx);
  }, [form]);

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

  const startDisplay = firstOpenDay?.pickup_start_time || "00:00:00";
  const [sHH = "00", sMM = "00"] = startDisplay.split(":");
  const discardDisplay = firstOpenDay?.pickup_end_time || "00:00:00";
  const [dHH = "00", dMM = "00"] = discardDisplay.split(":");

  const resetStartOffset = () => {
    const init = initialOffsetsRef.current?.start ?? { hour: 0, min: 0 };
    setPickupStartOffset(init.hour, init.min);
  };
  const resetDiscardOffset = () => {
    const init = initialOffsetsRef.current?.discard ?? { hour: 0, min: 0 };
    setPickupDiscardOffset(0, Math.min(60, Math.max(0, init.min)));
  };

  const onStartHourChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setPickupStartOffset(clampNum(e.target.value, 23), pickupStartOffset.min);
  };
  const onStartMinChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setPickupStartOffset(pickupStartOffset.hour, clampNum(e.target.value, 59));
  };
  const onDiscardMinChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setPickupDiscardOffset(0, clampNum(e.target.value, 60));
  };

  return (
    <div className="flex flex-col gap-y-[20px]">
      {/* 픽업 시작 기준 */}
      <div className="flex flex-col gap-y-[10px]">
        <h3>픽업 시간</h3>
        <div className="bodyFont">마감 세일을 시작할 시간을 입력해주세요.</div>
        <div className="text-center w-full justify-center">
          <div className="flex flex-row text-[20px] justify-center items-center gap-x-[10px]">
            <input
              className="bg-[#E7E7E7] rounded-sm w-[50px] h-[44px] text-center"
              value={pickupStartOffset.hour}
              onChange={onStartHourChange}
              inputMode="numeric"
              placeholder="hh"
            />
            <div>시</div>
            <input
              className="bg-[#E7E7E7] rounded-sm w-[50px] h-[44px] text-center"
              value={pickupStartOffset.min}
              onChange={onStartMinChange}
              inputMode="numeric"
              placeholder="mm"
            />
            <div>분 전부터</div>
          </div>
        </div>
        <div className="text-center hintFont">
          손님들이 {sHH}시 {sMM}분부터 매장에 방문하여 <br />
          패키지를 픽업할 수 있습니다.
        </div>
        <div className="flex justify-end gap-3 btnFont">
          <button
            type="button"
            className="text-main-deep"
            onClick={resetStartOffset}
          >
            초기화
          </button>
        </div>
      </div>

      {/* 픽업 마감 기준 */}
      <div className="flex flex-col gap-y-[10px]">
        <h3>픽업 마감 시간</h3>
        <div className="bodyFont">픽업을 마감할 시간을 입력해주세요.</div>
        <div className="text-center w-full justify-center">
          <div className="flex flex-row text-[20px] justify-center items-center gap-x-[10px]">
            <input
              className="bg-[#E7E7E7] rounded-sm w-[50px] h-[44px] text-center"
              value={pickupDiscardOffset.min}
              onChange={onDiscardMinChange}
              inputMode="numeric"
              placeholder="mm"
            />
            <div>분 전부터</div>
          </div>
        </div>
        <div className="hintFont text-center">
          {dHH}시 {dMM}분까지 픽업되지 않은 패키지는 폐기합니다.
        </div>
        <div className="flex justify-end gap-3 btnFont">
          <button
            type="button"
            className="text-main-deep"
            onClick={resetDiscardOffset}
          >
            초기화
          </button>
        </div>
      </div>
    </div>
  );
};

export default CommonPuTime;
