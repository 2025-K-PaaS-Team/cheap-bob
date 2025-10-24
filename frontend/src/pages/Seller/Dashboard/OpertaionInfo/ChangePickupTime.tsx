import { CommonBtn, CommonModal } from "@components/common";
import CommonLoading from "@components/common/CommonLoading";
import { CommonPuTime } from "@components/seller/common";
import { useToast } from "@context";
import type { OperationTimeType, StoreOperationType, Offset } from "@interface";
import {
  DeleteOperationReservation,
  GetStoreOperation,
  GetStoreOpReservation,
} from "@services";
import { CreateOperationReservation } from "@services";
import {
  formatErrMsg,
  fromMinutes,
  minusOffset,
  pad2,
  toHM,
  toMinutes,
} from "@utils";
import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";

const ChangePickupTime = () => {
  const { showToast } = useToast();
  const navigate = useNavigate();

  const [orig, setOrig] = useState<StoreOperationType>([]);
  const [form, setForm] = useState<OperationTimeType[]>([]);
  const [modiForm, setModiForm] = useState<OperationTimeType[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  const [pickupStartOffset, _setPickupStartOffset] = useState<Offset>({
    hour: 0,
    min: 0,
  });
  const [pickupDiscardOffset, _setPickupDiscardOffset] = useState<Offset>({
    hour: 0,
    min: 0,
  });

  const [showModal, setShowModal] = useState(false);
  const [modalMsg, setModalMsg] = useState("");

  const hasAll7 = useMemo(() => {
    const s = new Set(form.map((d) => d.day_of_week));
    return [0, 1, 2, 3, 4, 5, 6].every((v) => s.has(v));
  }, [form]);

  const setPickupStartOffset = (hour: number, min: number) => {
    _setPickupStartOffset({ hour, min });
  };
  const setPickupDiscardOffset = (hour: number, min: number) => {
    _setPickupDiscardOffset({ hour, min });
  };

  const load = async () => {
    try {
      const res = await GetStoreOperation();
      setOrig(res);

      // set form
      const initial: OperationTimeType[] = res
        .slice()
        .sort((a, b) => a.day_of_week - b.day_of_week)
        .map((d) => ({
          day_of_week: d.day_of_week,
          is_open_enabled: d.is_open_enabled,
          is_currently_open: d.is_currently_open,
          open_time: d.open_time ?? "",
          close_time: d.close_time ?? "",
          pickup_start_time: d.pickup_start_time ?? "",
          pickup_end_time: d.pickup_end_time ?? "",
        }));
      setForm(initial);

      // set modi form
      const modiRes = await GetStoreOpReservation();
      const modiInitial: OperationTimeType[] = modiRes.modifications
        .slice()
        .sort((a, b) => a.day_of_week - b.day_of_week)
        .map((d) => {
          const { h: ch, m: cm } = toHM(d.new_close_time);

          const startOffset = modiRes.new_pickup_start_interval ?? 0;
          const endOffset = modiRes.new_pickup_end_interval ?? 0;

          const startTime = minusOffset(
            ch,
            cm,
            Math.floor(startOffset / 60),
            startOffset % 60
          );
          const endTime = minusOffset(
            ch,
            cm,
            Math.floor(endOffset / 60),
            endOffset % 60
          );

          const pickup_start_time = `${pad2(startTime.h)}:${pad2(
            startTime.m
          )}:00`;
          const pickup_end_time = `${pad2(endTime.h)}:${pad2(endTime.m)}:00`;

          return {
            day_of_week: d.day_of_week,
            is_open_enabled: d.new_is_open_enabled,
            open_time: d.new_open_time,
            close_time: d.new_close_time,
            pickup_start_time,
            pickup_end_time,
          };
        });

      setModiForm(modiInitial);

      const firstOpen = modiInitial.find((d) => d.is_open_enabled !== false);
      if (firstOpen) {
        _setPickupStartOffset({
          hour: Math.floor((modiRes.new_pickup_start_interval ?? 0) / 60),
          min: (modiRes.new_pickup_start_interval ?? 0) % 60,
        });
        _setPickupDiscardOffset({
          hour: Math.floor((modiRes.new_pickup_end_interval ?? 0) / 60),
          min: (modiRes.new_pickup_end_interval ?? 0) % 60,
        });
      } else {
        _setPickupStartOffset({ hour: 0, min: 0 });
        _setPickupDiscardOffset({ hour: 0, min: 0 });
      }
    } catch {
      setModalMsg("운영 정보를 불러오는 것에 실패했습니다.");
      setShowModal(true);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const handleSubmit = async () => {
    if (!hasAll7) {
      setModalMsg("월~일 모든 요일의 정보가 포함되어야 합니다.");
      setShowModal(true);
      return;
    }

    const startOffset = pickupStartOffset.hour * 60 + pickupStartOffset.min;
    const endOffset = pickupDiscardOffset.hour * 60 + pickupDiscardOffset.min;

    const merged: StoreOperationType = orig.map((d) => {
      const f = modiForm.find((x) => x.day_of_week === d.day_of_week)!;
      const closeMin = toMinutes(f.close_time);

      if (closeMin === null) {
        return {
          ...d,
          is_open_enabled: f.is_open_enabled,
          open_time: f.open_time,
          close_time: f.close_time,
          pickup_start_time: d.pickup_start_time,
          pickup_end_time: d.pickup_end_time,
        };
      }

      const pickupStartMin = Math.max(closeMin - startOffset, 0);
      const pickupEndMin = Math.max(closeMin - endOffset, 0);

      return {
        ...d,
        is_open_enabled: f.is_open_enabled,
        open_time: f.open_time,
        close_time: f.close_time,
        pickup_start_time: fromMinutes(pickupStartMin),
        pickup_end_time: fromMinutes(pickupEndMin),
      };
    });

    for (const day of merged) {
      if (!day.close_time || !day.pickup_start_time) continue;

      const { h: ch, m: cm } = toHM(day.close_time);
      const { h: sh, m: sm } = toHM(day.pickup_start_time);

      const closeMinutes = ch * 60 + cm;
      const startMinutes = sh * 60 + sm;

      if (startMinutes > closeMinutes - 90) {
        setModalMsg(
          "픽업 시작 시간은 마감 시간으로부터 1시간 30분 이전이어야 합니다."
        );
        setShowModal(true);
        return;
      }
    }

    // delete origin reservation
    try {
      await DeleteOperationReservation();
      await new Promise((resolve) => setTimeout(resolve, 300));
    } catch (err) {
      console.warn("삭제 중 에러 발생:", err);
    }

    try {
      await CreateOperationReservation({ operation_times: merged });
      showToast("픽업 시간 변경에 성공했어요.", "success");
      navigate(-1);
    } catch (err) {
      setModalMsg(formatErrMsg(err));
      setShowModal(true);
    }
  };

  if (isLoading) {
    return <CommonLoading type="data" isLoading={isLoading} />;
  }

  return (
    <div className="flex flex-col flex-1 gap-y-[20px] p-[20px]">
      <div className="flex flex-1 flex-col gap-y-[20px]">
        <CommonPuTime
          form={modiForm}
          setForm={setModiForm}
          pickupStartOffset={pickupStartOffset}
          setPickupStartOffset={setPickupStartOffset}
          pickupDiscardOffset={pickupDiscardOffset}
          setPickupDiscardOffset={setPickupDiscardOffset}
        />
      </div>
      {/* 공지 */}
      <div className="w-full hintFont bg-[#E7E7E7] rounded px-[10px] h-[57px] flex items-center text-custom-black">
        변경사항은 다음 영업일부터 적용됩니다.
      </div>
      {/* btn */}
      <CommonBtn
        label="저장"
        onClick={handleSubmit}
        notBottom
        category="green"
      />

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

export default ChangePickupTime;
