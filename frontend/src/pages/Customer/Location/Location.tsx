const Location = () => {
  return (
    <div className="flex w-full flex-col">
      {/* now service */}
      <div className="mx-[20px] mb-[46px]">
        <div className="bg-[#F0F0F0] h-[52px] text-center flex items-center px-[12px]">
          <img
            src="/icon/greyCross.svg"
            alt="greyCrossIcon"
            className="pr-[12px] text-[#6C6C6C] text-[12px]"
          />
          현재는 관악구 지역만 서비스하고 있어요.
        </div>
      </div>
      {/* location table */}
      <div className="grid grid-rows-[32px_1fr] h-full border border-[#222222]">
        {/* Header Row */}
        <div className="grid grid-cols-3 text-center">
          <div className="bg-[#F0F0F0] border border-[#BFBFBF] text-[11px] flex items-center justify-center">
            시 · 도
          </div>
          <div className="bg-[#F0F0F0] border border-[#BFBFBF] text-[11px] flex items-center justify-center">
            시 · 군 · 구
          </div>
          <div className="bg-[#F0F0F0] border border-[#BFBFBF] text-[11px] flex items-center justify-center">
            동 · 읍 · 면
          </div>
        </div>

        {/* Content Row */}
        <div className="grid grid-cols-3">
          <div className="border border-[#BFBFBF] flex items-center justify-center">
            (시 · 도 데이터)
          </div>
          <div className="border border-[#BFBFBF] flex items-center justify-center">
            (시 · 군 · 구 데이터)
          </div>
          <div className="border border-[#BFBFBF] flex items-center justify-center">
            (동 · 읍 · 면 데이터)
          </div>
        </div>
      </div>
    </div>
  );
};

export default Location;
