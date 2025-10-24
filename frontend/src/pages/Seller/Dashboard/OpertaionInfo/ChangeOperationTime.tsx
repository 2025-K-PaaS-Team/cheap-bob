// pages/ChangeOperationTime.tsx
import { CommonBtn } from "@components/common";
import CommonLoading from "@components/common/CommonLoading";
import { CommonOpTime } from "@components/seller/common";
import { useToast } from "@context";
import type { StoreOperationType, OperationTimeType } from "@interface";
import {
  GetStoreOperation,
  CreateOperationReservation,
  GetStoreOpReservation,
  DeleteOperationReservation,
} from "@services";
import { diffFromClose, formatErrMsg, fromMinutes, toMinutes } from "@utils";
import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";

const ChangeOperationTime = () => {
  const { showToast } = useToast();
  const navigate = useNavigate();

  const [orig, setOrig] = useState<StoreOperationType>([]);
  const [form, setForm] = useState<OperationTimeType[]>([]);
  const [modiForm, setModiForm] = useState<OperationTimeType[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  const isComplete7 = useMemo(() => {
    const set = new Set(form.map((d) => d.day_of_week));
    return [0, 1, 2, 3, 4, 5, 6].every((v) => set.has(v));
  }, [form]);

  const getValid = (ops: OperationTimeType[]) => {
    return ops.some((op) => op.is_open_enabled === true);
  };

  const load = async () => {
    try {
      const res = await GetStoreOperation();
      setOrig(res);

      const initial = res
        .slice()
        .sort((a, b) => a.day_of_week - b.day_of_week)
        .map((d) => ({
          day_of_week: d.day_of_week,
          is_open_enabled: d.is_open_enabled,
          is_currently_open: d.is_currently_open,
          open_time: d.open_time,
          close_time: d.close_time,
          pickup_start_time: d.pickup_start_time ?? "",
          pickup_end_time: d.pickup_end_time ?? "",
        }));
      setForm(initial);

      // set modi form
      const modiRes = await GetStoreOpReservation();
      const modiInitial = modiRes.modifications
        .slice()
        .sort((a, b) => a.day_of_week - b.day_of_week)
        .map((d) => ({
          day_of_week: d.day_of_week,
          is_open_enabled: d.new_is_open_enabled,
          open_time: d.new_open_time,
          close_time: d.new_close_time,
          pickup_start_time: d.new_pickup_start_time ?? "",
          pickup_end_time: d.new_pickup_end_time ?? "",
        }));
      setModiForm(modiInitial);
    } catch (err) {
      showToast("운영 정보를 불러오는 데 실패했습니다.", "error");
      console.warn(err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  if (isLoading) {
    return <CommonLoading type="data" isLoading={isLoading} />;
  }

  const handleSubmit = async () => {
    if (!isComplete7) {
      showToast("월~일 모든 요일의 정보가 포함되어야 합니다.", "error");
      return;
    }

    const gapByDay = new Map<
      number,
      { gapStart: number | null; gapEnd: number | null }
    >();
    orig.forEach((d) => {
      const gapStart = diffFromClose(d.close_time, d.pickup_start_time);
      const gapEnd = diffFromClose(d.close_time, d.pickup_end_time);
      gapByDay.set(d.day_of_week, { gapStart, gapEnd });
    });

    const merged: StoreOperationType = orig.map((d) => {
      const f = modiForm.find((x) => x.day_of_week === d.day_of_week)!;
      const newCloseMin = toMinutes(f.close_time);
      const gaps = gapByDay.get(d.day_of_week) ?? {
        gapStart: null,
        gapEnd: null,
      };

      let nextPickupStart = d.pickup_start_time;
      let nextPickupEnd = d.pickup_end_time;

      if (newCloseMin != null) {
        if (gaps.gapStart != null)
          nextPickupStart = fromMinutes(newCloseMin - gaps.gapStart);
        if (gaps.gapEnd != null)
          nextPickupEnd = fromMinutes(newCloseMin - gaps.gapEnd);
      }

      return {
        ...d,
        is_open_enabled: f.is_open_enabled,
        open_time: f.open_time,
        close_time: f.close_time,
        pickup_start_time: nextPickupStart,
        pickup_end_time: nextPickupEnd,
      };
    });

    // delete origin reservation
    try {
      await DeleteOperationReservation();
      await new Promise((resolve) => setTimeout(resolve, 300));
    } catch (err) {
      console.warn("삭제 중 에러 발생:", err);
    }

    // create reservation
    try {
      await CreateOperationReservation({ operation_times: merged });
      showToast("영업 시간 변경에 성공했어요.", "success");
      navigate(-1);
    } catch (err) {
      showToast(formatErrMsg(err), "error");
      console.warn(err);
    }
  };

  return (
    <div className="px-[20px] my-[30px] flex flex-col gap-y-[20px]">
      <div className="flex flex-col flex-1 gap-y-[20px]">
        <CommonOpTime originForm={form} form={modiForm} setForm={setModiForm} />
      </div>

      <div className="w-full hintFont bg-[#E7E7E7] rounded px-[10px] h-[57px] flex items-center text-custom-black">
        변경사항은 다음 영업일부터 적용됩니다.
      </div>

      <CommonBtn
        label="저장"
        onClick={handleSubmit}
        category={getValid(form) ? "green" : "grey"}
        notBottom
      />
    </div>
  );
};

export default ChangeOperationTime;
