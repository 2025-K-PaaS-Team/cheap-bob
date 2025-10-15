import { CommonBtn, CommonModal } from "@components/common";
import { CommonPuTime } from "@components/seller/common";
import type { OperationTimeType, StoreOperationType, Offset } from "@interface";
import { GetStoreOperation } from "@services";
import { CreateOperationReservation } from "@services";
import { diffFromClose, minutesToOffset } from "@utils";
import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router";

const ChangePickupTime = () => {
  const navigate = useNavigate();

  const [orig, setOrig] = useState<StoreOperationType>([]);
  const [form, setForm] = useState<OperationTimeType[]>([]);
  const [loading, setLoading] = useState(true);

  // 오프셋(마감에서 몇 분 전부터 시작/폐기)
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

  // 7개 요일 모두 있는지
  const hasAll7 = useMemo(() => {
    const s = new Set(form.map((d) => d.day_of_week));
    return [0, 1, 2, 3, 4, 5, 6].every((v) => s.has(v));
  }, [form]);

  // 오프셋 setter (CommonPuTime이 요구하는 시그니처)
  const setPickupStartOffset = (hour: number, min: number) => {
    _setPickupStartOffset({ hour, min });
  };
  const setPickupDiscardOffset = (hour: number, min: number) => {
    _setPickupDiscardOffset({ hour, min });
  };

  // 초기 로드: 기존 값으로 form 초기화 + 오프셋 초기값 설정
  const load = async () => {
    try {
      const res = await GetStoreOperation(); // StoreOperationType (length 7)
      setOrig(res);

      // form 초기값: 서버값 그대로(픽업/오픈/마감/활성여부 포함)
      const initial: OperationTimeType[] = res
        .slice()
        .sort((a, b) => a.day_of_week - b.day_of_week)
        .map((d) => ({
          day_of_week: d.day_of_week,
          is_open_enabled: d.is_open_enabled,
          open_time: d.open_time ?? "",
          close_time: d.close_time ?? "",
          pickup_start_time: d.pickup_start_time ?? "",
          pickup_end_time: d.pickup_end_time ?? "",
        }));
      setForm(initial);

      // 오프셋 초기화: 첫 번째 활성 요일 기준으로 close - pickup 간격을 계산해서 사용
      const firstOpen = initial.find((d) => d.is_open_enabled !== false);
      if (firstOpen) {
        const gapStart = diffFromClose(
          firstOpen.close_time,
          firstOpen.pickup_start_time
        );
        const gapEnd = diffFromClose(
          firstOpen.close_time,
          firstOpen.pickup_end_time
        );
        _setPickupStartOffset(minutesToOffset(gapStart));
        _setPickupDiscardOffset(minutesToOffset(gapEnd));
      } else {
        _setPickupStartOffset({ hour: 0, min: 0 });
        _setPickupDiscardOffset({ hour: 0, min: 0 });
      }
    } catch {
      setModalMsg("운영 정보를 불러오는 것에 실패했습니다.");
      setShowModal(true);
    } finally {
      setLoading(false);
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

    // 이 화면은 "픽업 시간만" 변경. open/close/is_open_enabled는 기존(orig) 그대로,
    // 픽업 시간은 form(=오프셋 반영 결과)에서 가져옴.
    const merged: OperationTimeType[] = orig.map((d) => {
      const f = form.find((x) => x.day_of_week === d.day_of_week)!;
      return {
        day_of_week: d.day_of_week,
        is_open_enabled: d.is_open_enabled, // 운영여부는 변경 안 함(원하면 f로 교체)
        open_time: d.open_time,
        close_time: d.close_time,
        pickup_start_time: f.pickup_start_time,
        pickup_end_time: f.pickup_end_time,
      };
    });

    try {
      // 문서 스펙: { operation_times: OperationTimeType[] }
      await CreateOperationReservation({ operation_times: merged });
      navigate(-1);
    } catch {
      setModalMsg("예약 저장에 실패했습니다. 입력값을 확인해 주세요.");
      setShowModal(true);
    }
  };

  if (loading) {
    return <div className="mx-[20px] mt-[40px]">로딩중…</div>;
  }

  return (
    <div className="flex flex-col gap-y-[10px] mx-[20px]">
      {/* Pickup 편집: 오프셋으로 모든 요일의 pickup_* 자동 계산 */}
      <CommonPuTime
        form={form}
        setForm={setForm}
        pickupStartOffset={pickupStartOffset}
        setPickupStartOffset={setPickupStartOffset}
        pickupDiscardOffset={pickupDiscardOffset}
        setPickupDiscardOffset={setPickupDiscardOffset}
      />

      {/* notice */}
      <div className="absolute bottom-30 w-[350px] left-1/2 -translate-x-1/2 bg-custom-white rounded-[8px] h-[57px] px-[10px] flex items-center">
        변경시 다음 영업일부터 적용됩니다.
      </div>

      {/* btn */}
      <CommonBtn label="저장" onClick={handleSubmit} category="black" />

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

export default ChangePickupTime;
