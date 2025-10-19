type ProfileProps = {
  nickname: string;
  phone: string;
  nutrition_goal: string[];
  prefer_menu: string[];
  prefer_topping: string[];
  allergy: string[];
  onCancelClick: () => void;
};

const CommonProfile = ({
  nickname,
  phone,
  nutrition_goal,
  prefer_menu,
  prefer_topping,
  allergy,
  onCancelClick,
}: ProfileProps) => {
  return (
    <div className="fixed inset-0 flex flex-col items-center justify-center bg-black/50 z-50">
      <div className="bg-white rounded-t flex flex-col border-b border-black/80 w-[322px] px-[16px] py-[20px] gap-y-[8px]">
        {/* first row - white zone */}
        <div className="flex flex-row justify-between">
          <h1>{nickname}</h1>
          <img src="/icon/cross.svg" alt="crossIcon" onClick={onCancelClick} />
        </div>
        {/* second row - white zone */}
        <div className="bodyFont text-custom-black">전화번호 {phone}</div>
      </div>

      {/* other row - custom white zone */}
      <div className="bg-custom-white rounded-b flex flex-col w-[322px] px-[16px] py-[20px] justify-start gap-y-[8px]">
        {/* nutrition_part */}
        <div className="bodyFont text-custom-black">영양 목표</div>
        <div className="flex flex-row flex-wrap gap-x-[10px] gap-y-[10px]">
          {nutrition_goal.map((part, idx) => (
            <div
              key={idx}
              className="bg-main-pale text-main-deep w-fit border border-main-deep rounded py-[7px] px-[16px] tagFont font-bold"
            >
              {part}
            </div>
          ))}
        </div>

        {/* prefer_menu */}
        <div className="bodyFont text-custom-black">선호 메뉴</div>
        <div className="flex flex-row flex-wrap gap-x-[10px] gap-y-[10px]">
          {prefer_menu.map((part, idx) => (
            <div
              key={idx}
              className="bg-main-pale text-main-deep w-fit border border-main-deep rounded py-[7px] px-[16px] tagFont font-bold"
            >
              {part}
            </div>
          ))}
        </div>

        {/* prefer_topping */}
        <div className="bodyFont text-custom-black">선호 토핑</div>
        <div className="flex flex-row flex-wrap gap-x-[10px] gap-y-[10px]">
          {prefer_topping.map((part, idx) => (
            <div
              key={idx}
              className="bg-main-pale text-main-deep w-fit border border-main-deep rounded py-[7px] px-[16px] tagFont font-bold"
            >
              {part}
            </div>
          ))}
        </div>

        {/* allergy */}
        <div className="bodyFont text-custom-black">알레르기</div>
        <div className="flex flex-row flex-wrap gap-x-[10px] gap-y-[10px]">
          {allergy.map((part, idx) => (
            <div
              key={idx}
              className="bg-[#e7e7e7] text-custom-black w-fit rounded py-[7px] px-[16px] tagFont font-bold"
            >
              {part}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default CommonProfile;
