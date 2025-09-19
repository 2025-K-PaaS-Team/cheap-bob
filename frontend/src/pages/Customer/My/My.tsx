const My = () => {
  return (
    <div className="px-[20px] w-full">
      {/* order history & nutrition goal */}
      <div className="grid grid-cols-2 gap-x-[10px] pt-[14px] pb-[95px]">
        <div className="flex flex-col bg-[#717171] p-[15px] text-white rounded-[5px] h-[109px]">
          <div className="font-semibold text-[15px]">주문 내역</div>
        </div>
        <div className="flex flex-col bg-[#717171] p-[15px] text-white rounded-[5px] h-[109px]">
          <div className="font-semibold text-[15px]">영양 목표</div>
        </div>
      </div>
      {/* policy */}
      <div className="text-[15px] py-[20px] font-bold">약관 및 정책</div>
      {/* connect to seller */}
      <div className="text-[15px] py-[20px] font-bold">사장님으로 접속</div>
      {/* logout */}
      <div className="text-[15px] py-[20px] font-bold">로그아웃</div>
      {/* withdraw member */}
      <div className="text-[15px] py-[20px] font-bold">계정탈퇴</div>
    </div>
  );
};

export default My;
