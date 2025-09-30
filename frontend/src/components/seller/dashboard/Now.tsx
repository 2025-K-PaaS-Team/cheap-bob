const NowStatus = () => {
  return (
    <div className="mx-[20px] flex flex-col gap-y-[3px] mt-[7px] bg-[#3A3A3A] rounded-[8px] py-[25px] px-[19px] text-white">
      <div className="text-[24px]">
        지금은 <span className="font-bold">운영중</span> 입니다.
      </div>
      <div className="text-[20px]">손님 픽업 시간까지 1시간 29분</div>
      <div className="text-[16px]">영업 상태 변경 &gt;</div>
    </div>
  );
};

export default NowStatus;
