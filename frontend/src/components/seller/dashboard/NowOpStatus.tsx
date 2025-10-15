import { CommonDropbox, CommonModal } from "@components/common";
import { OpStatusOption } from "@constant";
import type { OperationTimeType } from "@interface";
import type { OptionType } from "@interface/common/types";
import { useState } from "react";

const toMin = (t?: string) => {
  if (!t) return null;
  const [h, m] = t.split(":").map((v) => parseInt(v, 10));
  if (Number.isNaN(h) || Number.isNaN(m)) return null;
  return h * 60 + m;
};

const fmtDur = (mm: number) => {
  if (mm <= 0) return "0분";
  const h = Math.floor(mm / 60);
  const m = mm % 60;
  if (h && m) return `${h}시간 ${m}분`;
  if (h) return `${h}시간`;
  return `${m}분`;
};

const jsToServerDow = (jsDay: number) => (jsDay + 6) % 7;

const normalizeSpan = (openMin: number, closeMin: number) => {
  if (closeMin >= openMin)
    return { open: openMin, close: closeMin, cross: false };
  return { open: openMin, close: closeMin + 1440, cross: true };
};

type Props = {
  ops: OperationTimeType[];
};

const NowOpStatus = ({ ops }: Props) => {
  const now = new Date();
  const jsDay = now.getDay();
  const dow = jsToServerDow(jsDay);
  const currMin = now.getHours() * 60 + now.getMinutes();
  const [openChangeModal, setOpenChangeModal] = useState<boolean>(false);

  const handleConfirmChange = () => {
    setOpenChangeModal(false);
  };

  const today = ops.find((o) => o.day_of_week === dow);
  const enabledToday = today?.is_open_enabled;

  let title = "지금은 영업 전입니다.";
  let sub = "";

  if (!today) {
    return (
      <div className="mx-[20px] flex flex-col gap-y-[3px] mt-[7px] bg-[#393939] rounded-[8px] py-[25px] px-[19px] text-white">
        <div className="text-[24px]">{title}</div>
        {sub && <div className="text-[20px]">{sub}</div>}
        <div className="text-[16px]">영업 상태 변경 &gt;</div>
      </div>
    );
  }

  const o = toMin(today.open_time) ?? 0;
  const c = toMin(today.close_time) ?? 0;
  const s = toMin(today.pickup_start_time) ?? null;
  const e = toMin(today.pickup_end_time) ?? null;

  const { open, close } = normalizeSpan(o, c);

  const current = currMin < open ? currMin + 1440 : currMin;

  if (!enabledToday) {
    title = "오늘은 휴무입니다.";
  } else {
    if (current < open) {
      title = "지금은 영업 전입니다.";
      sub = `영업 시작까지 ${fmtDur(open - current)}`;
    } else if (current >= open && current < close) {
      title = "지금은 운영중 입니다.";

      if (s != null && e != null) {
        const sN = s < open ? s + 1440 : s;
        const eN = e < open ? e + 1440 : e;

        if (current < sN) {
          sub = `손님 픽업 시간까지 ${fmtDur(sN - current)}`;
        } else if (current >= sN && current < eN) {
          sub = `픽업 마감까지 ${fmtDur(eN - current)}`;
        } else {
          sub = "오늘 픽업이 종료되었습니다.";
        }
      } else {
        sub = `영업 마감까지 ${fmtDur(close - current)}`;
      }
    } else {
      title = "지금은 운영 종료입니다.";
      sub = "";
    }
  }

  const [selectedOption, setSelectedOption] = useState<OptionType | null>(null);

  return (
    <>
      <div className="mx-[20px] flex flex-col gap-y-[3px] mt-[7px] bg-[#393939] rounded-[8px] py-[25px] px-[19px] text-white">
        <div className="text-[24px]">{title}</div>
        {sub && <div className="text-[20px]">{sub}</div>}
        <div className="text-[16px]" onClick={() => setOpenChangeModal(true)}>
          영업 상태 변경 &gt;
        </div>
      </div>

      {openChangeModal && (
        <CommonModal
          cancelLabel="취소"
          confirmLabel="변경하기"
          desc="영업 상태 변경"
          onCancelClick={() => setOpenChangeModal(false)}
          onConfirmClick={() => handleConfirmChange()}
        >
          <CommonDropbox
            options={OpStatusOption}
            value={selectedOption}
            onChange={setSelectedOption}
          />
        </CommonModal>
      )}
    </>
  );
};

export default NowOpStatus;
