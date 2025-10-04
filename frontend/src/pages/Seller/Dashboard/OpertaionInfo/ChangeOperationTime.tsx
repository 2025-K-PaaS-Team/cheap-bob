// pages/ChangeOperationTime.tsx
import { CommonBtn, CommonModal } from "@components/common";
import { CommonOpTime } from "@components/seller/common";
import type { StoreOperationType, OperationTimeType } from "@interface";
import { GetStoreOperation } from "@services";
import { CreateOperationReservation } from "@services";
import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router";

// ---------- 시간 유틸 ----------
const toMinutes = (t?: string): number | null => {
  if (!t) return null;
  // 기대 포맷: "HH:MM:SS" or "HH:MM"
  const [hh = "", mm = ""] = t.split(":");
  const h = Number(hh);
  const m = Number(mm);
  if (Number.isNaN(h) || Number.isNaN(m)) return null;
  return (((h * 60 + m) % 1440) + 1440) % 1440;
};

const fromMinutes = (mins: number): string => {
  const m = ((mins % 1440) + 1440) % 1440;
  const hh = String(Math.floor(m / 60)).padStart(2, "0");
  const mm = String(m % 60).padStart(2, "0");
  return `${hh}:${mm}:00`;
};

// close - pickup 간격(분). 입력 중 하나라도 없으면 null
const diffFromClose = (close?: string, pickup?: string): number | null => {
  const c = toMinutes(close);
  const p = toMinutes(pickup);
  if (c == null || p == null) return null;
  return (c - p + 1440) % 1440; // 모듈러(자정 경계 안전)
};

const ChangeOperationTime = () => {
  const navigate = useNavigate();

  // 원본(서버 현재값) — pickup 간격 계산에 필요
  const [orig, setOrig] = useState<StoreOperationType>([]);
  // 화면에서 편집할 폼(open/close/is_open_enabled)
  const [form, setForm] = useState<OperationTimeType[]>([]);
  const [loading, setLoading] = useState(true);

  const [showModal, setShowModal] = useState(false);
  const [modalMsg, setModalMsg] = useState("");

  // 월~일 7개 포함 여부
  const isComplete7 = useMemo(() => {
    const set = new Set(form.map((d) => d.day_of_week));
    return [0, 1, 2, 3, 4, 5, 6].every((v) => set.has(v));
  }, [form]);

  // 최초 로드: 기존 운영 정보로 폼 초기화
  const load = async () => {
    try {
      const res = await GetStoreOperation();
      setOrig(res);

      // 폼은 open/close/is_open_enabled만 편집(초깃값 = 서버값)
      const initial = res
        .slice()
        .sort((a, b) => a.day_of_week - b.day_of_week)
        .map((d) => ({
          day_of_week: d.day_of_week,
          is_open_enabled: d.is_open_enabled,
          open_time: d.open_time,
          close_time: d.close_time,
          pickup_start_time: d.pickup_start_time ?? "",
          pickup_end_time: d.pickup_end_time ?? "",
        }));
      setForm(initial);
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

  // 제출: 기존 close↔pickup 간격 유지해서 pickup 재계산 후 예약 생성
  const handleSubmit = async () => {
    if (!isComplete7) {
      setModalMsg("월~일 모든 요일의 정보가 포함되어야 합니다.");
      setShowModal(true);
      return;
    }

    // 1) 요일별 기존 간격 계산
    const gapByDay = new Map<
      number,
      { gapStart: number | null; gapEnd: number | null }
    >();
    orig.forEach((d) => {
      const gapStart = diffFromClose(d.close_time, d.pickup_start_time);
      const gapEnd = diffFromClose(d.close_time, d.pickup_end_time);
      gapByDay.set(d.day_of_week, { gapStart, gapEnd });
    });

    // 2) 폼의 close_time 기준으로 pickup 재계산 후 병합
    const merged: StoreOperationType = orig.map((d) => {
      const f = form.find((x) => x.day_of_week === d.day_of_week)!;

      const newCloseMin = toMinutes(f.close_time);
      const gaps = gapByDay.get(d.day_of_week) ?? {
        gapStart: null,
        gapEnd: null,
      };

      let nextPickupStart = d.pickup_start_time;
      let nextPickupEnd = d.pickup_end_time;

      if (newCloseMin != null) {
        if (gaps.gapStart != null) {
          nextPickupStart = fromMinutes(newCloseMin - gaps.gapStart);
        }
        if (gaps.gapEnd != null) {
          nextPickupEnd = fromMinutes(newCloseMin - gaps.gapEnd);
        }
      }

      // 휴무일 처리(선택): 휴무면 픽업 비우고 싶다면 아래 주석 해제
      // if (!f.is_open_enabled) {
      //   nextPickupStart = "";
      //   nextPickupEnd = "";
      // }

      return {
        ...d,
        is_open_enabled: f.is_open_enabled,
        open_time: f.open_time,
        close_time: f.close_time,
        pickup_start_time: nextPickupStart,
        pickup_end_time: nextPickupEnd,
      };
    });

    try {
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
    <div className="relative flex h-full mx-[20px] flex-col">
      {/* 기존값으로 초기화된 폼을 CommonOpTime에 연결 */}
      <CommonOpTime form={form} setForm={setForm} />

      {/* 공지 */}
      <div className="absolute bottom-30 w-[350px] left-1/2 -translate-x-1/2 bg-[#d9d9d9] rounded-[8px] h-[57px] px-[10px] flex items-center">
        변경 시 다음 영업일부터 적용됩니다.
      </div>

      {/* 저장 */}
      <CommonBtn label="저장" onClick={handleSubmit} className="black" />

      {/* 모달 */}
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

export default ChangeOperationTime;
