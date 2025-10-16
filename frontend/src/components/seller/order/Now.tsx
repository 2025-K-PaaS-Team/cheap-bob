const NowStatus = () => {
  return (
    <div className="flex flex-col mx-[20px] my-[15px] gap-y-[15px]">
      <div className="flex flex-col bg-main-500 rounded-sm p-[17px]">
        <div className="text-[24px]">
          지금은 <span className="font-bold">픽업 시간</span> 입니다
        </div>
        <div className="text-[18px]">픽업 마감 시간까지 1시간 29분</div>
      </div>
      <div className="text-[14px] flex flex-row justify-between">
        <div>마지막 업데이트: 13시 25분</div>
        <div>새로고침 O</div>
      </div>
    </div>
  );
};

export default NowStatus;
