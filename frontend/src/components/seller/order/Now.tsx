import type { StoreOperationType } from "@interface";

interface NowStatusProps {
  onRefresh: () => void;
  lastUpdated: string;
  op: StoreOperationType;
}

const NowStatus = ({ onRefresh, lastUpdated, op }: NowStatusProps) => {
  // 현재 요일과 시간 가져오기
  const now = new Date();
  const currentDay = now.getDay(); // 0(일) ~ 6(토)
  const currentTime = now.toTimeString().slice(0, 8); // HH:mm:ss 형태

  const todayOp = op.find((item) => item.day_of_week === currentDay);

  let statusText = "로딩 중...";

  if (todayOp) {
    const {
      open_time,
      close_time,
      pickup_start_time,
      pickup_end_time,
      is_open_enabled,
    } = todayOp;

    if (!is_open_enabled) {
      statusText = "영업 전";
    } else if (currentTime < open_time) {
      statusText = "영업 전";
    } else if (currentTime >= open_time && currentTime < pickup_start_time) {
      statusText = "영업 시간";
    } else if (
      currentTime >= pickup_start_time &&
      currentTime < pickup_end_time
    ) {
      statusText = "픽업 시간";
    } else if (currentTime >= pickup_end_time && currentTime < close_time) {
      statusText = "마감 시간";
    } else {
      statusText = "영업 전";
    }
  }

  return (
    <div className="flex flex-col px-[20px] py-[16px] gap-y-[8px] bg-[#393939]">
      <div className="flex flex-col bg-main-500 rounded-sm">
        <div className="titleFont text-white">
          지금은 <span className="font-bold text-main-deep">{statusText}</span>{" "}
          입니다.
        </div>
      </div>
      <div className="hintFont text-[#9D9D9D] flex flex-row justify-between">
        <div>마지막 업데이트: {lastUpdated ? lastUpdated : "로딩 중..."}</div>
        <div
          onClick={onRefresh}
          className="flex flex-row gap-x-[8px] cursor-pointer"
        >
          화면 새로고침 <img src="/icon/refresh.svg" alt="refreshIcon" />
        </div>
      </div>
    </div>
  );
};

export default NowStatus;
