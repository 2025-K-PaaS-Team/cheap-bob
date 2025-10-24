import { CommonDropbox, CommonModal } from "@components/common";
import { OpStatusOption } from "@constant";
import type { OperationTimeType } from "@interface";
import type { OptionType } from "@interface/common/types";
import { CloseStore } from "@services";
import { useState, useMemo } from "react";

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

const normalizeSpan = (openMin: number, closeMin: number) =>
  closeMin >= openMin
    ? { open: openMin, close: closeMin, cross: false }
    : { open: openMin, close: closeMin + 1440, cross: true };

type Props = {
  ops: OperationTimeType[];
};

const NowOpStatus = ({ ops }: Props) => {
  const [openChangeModal, setOpenChangeModal] = useState(false);
  const [selectedOption, setSelectedOption] = useState<OptionType | null>(null);
  const [showModal, setShowModal] = useState<boolean>(false);
  const [modalMsg, setModalMsg] = useState("");

  const now = new Date();
  const dow = jsToServerDow(now.getDay());
  const currMin = now.getHours() * 60 + now.getMinutes();

  const today = ops.find((o) => o.day_of_week === dow);
  const enabledToday = today?.is_open_enabled ?? false;
  const currentOpenToday = today?.is_currently_open ?? false;

  const statusInfo = useMemo(() => {
    if (!today) return { title: "지금은 영업 전 입니다.", sub: "" };

    const o = toMin(today.open_time) ?? 0;
    const c = toMin(today.close_time) ?? 0;
    const s = toMin(today.pickup_start_time) ?? null;
    const e = toMin(today.pickup_end_time) ?? null;
    const { open, close } = normalizeSpan(o, c);
    const current = currMin < open ? currMin + 1440 : currMin;

    if (!enabledToday) {
      return { title: "오늘은 휴무 입니다.", sub: "" };
    }

    if (enabledToday && !currentOpenToday) {
      return { title: "오늘의 영업이 끝났습니다.", sub: "" };
    }

    if (current < open) {
      // 영업 전
      return {
        title: "지금은 영업 전 입니다.",
        sub: `오픈까지 ${fmtDur(open - current)}`,
      };
    }

    // 영업 중
    if (current >= open && current < close) {
      let sub = "";
      if (s != null && e != null) {
        const sN = s < open ? s + 1440 : s;
        const eN = e < open ? e + 1440 : e;

        if (current < sN) sub = `픽업 시간까지 ${fmtDur(sN - current)}`;
        else if (current < eN) sub = `픽업 마감까지 ${fmtDur(eN - current)}`;
        else sub = "오늘의 영업이 끝났습니다.";
      } else {
        sub = `영업 마감까지 ${fmtDur(close - current)}`;
      }
      return { title: "지금은 영업중 입니다.", sub };
    }

    // 영업 마감 이후
    return {
      title: "지금은 영업 마감 입니다.",
      sub: "오늘의 영업이 끝났습니다.",
    };
  }, [today, currMin, enabledToday]);

  const highlightStatus = (text: string) => {
    const statusWords = ["영업 전", "영업중", "운영 종료", "휴무"];
    let highlighted = text;
    statusWords.forEach((word) => {
      highlighted = highlighted.replace(
        word,
        `<span class='text-main-deep font-bold'>${word} </span>`
      );
    });
    return highlighted;
  };

  const handleChangeOpStatus = async () => {
    try {
      await CloseStore();
      setOpenChangeModal(false);
    } catch (err) {
      setModalMsg("영업 상태 변경에 실패했습니다.");
      setShowModal(true);
      return;
    }
  };

  return (
    <>
      <div className="mx-[20px] flex flex-col gap-y-[3px] mt-[7px] bg-[#393939] rounded-sm py-[25px] px-[19px] text-white">
        <div
          className="titleFont titleFont"
          dangerouslySetInnerHTML={{
            __html: highlightStatus(statusInfo.title),
          }}
        />
        {statusInfo.sub && <div className="text-[20px]">{statusInfo.sub}</div>}

        <div
          className="flex flex-row items-center"
          onClick={() => setOpenChangeModal(true)}
        >
          <div className="text-[16px]">영업 상태 변경</div>
          <img src="/icon/nextWhite.svg" alt="nextIcon" />
        </div>
      </div>

      {openChangeModal && (
        <CommonModal
          cancelLabel="취소"
          confirmLabel="변경하기"
          desc="영업 상태 변경"
          onCancelClick={() => setOpenChangeModal(false)}
          onConfirmClick={() => handleChangeOpStatus()}
        >
          <CommonDropbox
            options={OpStatusOption}
            value={selectedOption}
            onChange={setSelectedOption}
            placeholder="변경할 영업 상태를 선택해 주세요."
          />
        </CommonModal>
      )}

      {/* show modal */}
      {showModal && (
        <CommonModal
          desc={modalMsg}
          confirmLabel="확인"
          onConfirmClick={() => setShowModal(false)}
          category="green"
        />
      )}
    </>
  );
};

export default NowOpStatus;
