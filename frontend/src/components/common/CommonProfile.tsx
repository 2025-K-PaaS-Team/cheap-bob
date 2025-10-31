type ProfileProps = {
  nickname: string;
  phone: string;
  nutrition_goal: string[];
  prefer_menu: string[];
  prefer_topping: string[];
  allergy: string[];
  datetime: string;
  qty: number;
  onCancelClick: () => void;
};

const CommonProfile = ({
  nickname,
  phone,
  nutrition_goal,
  prefer_menu,
  prefer_topping,
  allergy,
  datetime,
  qty,
  onCancelClick,
}: ProfileProps) => {
  const reservationAt = new Date(datetime)
    .toLocaleString("ko-KR", {
      timeZone: "Asia/Seoul",
      year: "numeric",
      month: "2-digit",
      day: "2-digit",
      hour: "2-digit",
      minute: "2-digit",
      hour12: false,
    })
    .replace(/\.\s/g, ".")
    .replace(/\.$/, "")
    .replace(/\.(\d{2}:\d{2})$/, " $1");

  return (
    <div className="absolute inset-0 z-[1000] flex flex-col items-center justify-center bg-black/20">
      <div className="bg-white rounded-t flex flex-col border-b border-black/80 w-[322px] px-[16px] py-[20px] gap-y-[8px]">
        {/* first row - white zone */}
        <div className="flex flex-row relative tagFont font-bold">
          <div>{reservationAt}</div>·<div>{qty}개</div>
          <img
            src="/icon/cross.svg"
            alt="crossIcon"
            onClick={onCancelClick}
            className="absolute right-0 top-0"
          />
        </div>
        <h1>{nickname ?? ""}</h1>
        {/* second row - white zone */}
        <div className="bodyFont text-custom-black">전화번호 {phone ?? ""}</div>
      </div>

      {/* other row - custom white zone */}
      <div className="bg-custom-white rounded-b flex flex-col w-[322px] px-[16px] py-[20px] justify-start gap-y-[8px]">
        {/* nutrition_part */}
        <div className="bodyFont text-custom-black font-bold">영양 목표</div>
        <div className="flex flex-row flex-wrap gap-x-[10px] gap-y-[10px]">
          {nutrition_goal?.map((part, idx) => (
            <div
              key={idx}
              className="bg-main-pale text-main-deep w-fit border border-main-deep rounded py-[7px] px-[16px] tagFont font-bold"
            >
              {part}
            </div>
          )) ?? "등록한 영양 목표가 없습니다"}
        </div>

        {/* prefer_menu */}
        <div className="bodyFont text-custom-black font-bold">선호 메뉴</div>
        <div className="flex flex-row flex-wrap gap-x-[10px] gap-y-[10px]">
          {prefer_menu?.map((part, idx) => (
            <div
              key={idx}
              className="bg-main-pale text-main-deep w-fit border border-main-deep rounded py-[7px] px-[16px] tagFont font-bold"
            >
              {part}
            </div>
          )) ?? "등록한 선호 메뉴가 없습니다"}
        </div>

        {/* prefer_topping */}
        <div className="bodyFont text-custom-black font-bold">선호 토핑</div>
        <div className="flex flex-row flex-wrap gap-x-[10px] gap-y-[10px]">
          {prefer_topping?.map((part, idx) => (
            <div
              key={idx}
              className="bg-main-pale text-main-deep w-fit border border-main-deep rounded py-[7px] px-[16px] tagFont font-bold"
            >
              {part}
            </div>
          )) ?? "등록한 선호 토핑이 없습니다"}
        </div>

        {/* allergy */}
        <div className="bodyFont text-custom-black font-bold">알레르기</div>
        <div className="flex flex-row flex-wrap gap-x-[10px] gap-y-[10px]">
          {allergy?.map((part, idx) => (
            <div
              key={idx}
              className="bg-[#e7e7e7] text-custom-black w-fit rounded py-[7px] px-[16px] tagFont font-bold"
            >
              {part}
            </div>
          )) ?? "등록한 알러지가 없습니다"}
        </div>
      </div>
    </div>
  );
};

export default CommonProfile;
