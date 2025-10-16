const NowStatus = () => {
  return (
    <div className="flex flex-col px-[20px] py-[16px] gap-y-[8px] bg-[#393939]">
      <div className="flex flex-col bg-main-500 rounded-sm">
        <div className="titleFont text-white">
          지금은 <span className="font-bold text-main-deep">픽업 시간</span>{" "}
          입니다
        </div>
      </div>
      <div className="hintFont text-[#9D9D9D] flex flex-row justify-between">
        <div>마지막 업데이트: 13시 25분</div>
        <div>새로고침 O</div>
      </div>
    </div>
  );
};

export default NowStatus;
