const Dashboard = () => {
  return (
    <div className="flex w-full flex-col px-[20px]">
      {/* now operating status */}
      <div className="flex flex-col gap-y-[3px] mt-[7px] bg-[#3A3A3A] rounded-[8px] py-[25px] px-[19px] text-white">
        <div className="text-[24px]">
          지금은 <span className="font-bold">운영중</span> 입니다.
        </div>
        <div className="text-[20px]">손님 픽업 시간까지 1시간 29분</div>
        <div className="text-[16px]">영업 상태 변경 &gt;</div>
      </div>

      {/* remaining package quantity */}
      <div className="flex flex-col mt-[7px] bg-[#D9D9D9] rounded-[8px] py-[23px] px-[19px] text-black">
        <div className="text-[24px] mb-[7px]">
          현재 패키지 잔여 수량은 <br /> <span className="font-bold">2개</span>{" "}
          입니다.
        </div>
        <div className="grid grid-cols-4 text-center gap-x-[11px]">
          <div className="flex flex-col py-[14px]">
            <div className="text-[14px]">판매 기본값</div>
            <div className="text-[24px]">5</div>
          </div>
          <div className="flex flex-col py-[14px]">
            <div className="text-[14px]">- 픽업 확정</div>
            <div className="text-[24px]">-2</div>
          </div>
          <div className="relative py-[14px] flex flex-row col-span-2 bg-[#969696] rounded-[8px] justify-center">
            <div className="flex flex-col justify-center">
              <div className="text-[14px]">+ 일일 조정값</div>
              <div className="text-[24px]">-1</div>
            </div>
            <div className="absolute right-[10px] top-[31px] flex flex-col justify-center gap-y-[4px]">
              <div className="bg-white w-[20px] aspect-square flex items-center justify-center text-[10px] rounded-full">
                ▲
              </div>
              <div className="bg-white w-[20px] aspect-square flex items-center justify-center text-[10px] rounded-full">
                ▼
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
