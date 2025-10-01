const BillingHistory = () => {
  return (
    <div className="flex flex-col">
      <div className="mx-[33px] flex flex-col gap-y-[35px] mt-[15px]">
        <div className="flex flex-row justify-around">
          <div className="font-bold">기간</div>
          <div className="bg-[#d9d9d9] w-[103px] h-[30px]"></div>
          <div className="font-bold">~</div>
          <div className="bg-[#d9d9d9] w-[103px] h-[30px]"></div>
        </div>
        <div className="flex flex-row justify-around">
          <div className="font-bold">상태</div>
          <div className="">전체보기</div>
          <div className="">정산 완료</div>
          <div className="">환불 완료</div>
        </div>
      </div>

      {/* divider */}
      <hr className="border-0 h-[1px] bg-black/20 mt-[35px] mb-[17px]" />

      {/* order history */}
      <div className="flex flex-col mx-[27px] gap-y-[13px]">
        <div className="text-[14px]">n건의 주문 내역이 있습니다.</div>
        <div className="text-[16px] font-bold">25.09.08</div>
        <div className="bg-[#D9D9D9] rounded-[8px] px-[17px] py-[20px] text-[16px] gap-y-[7px] flex flex-col">
          <div className="justify-between flex-row flex">
            <div className="font-bold">(패키지 이름)</div>
            <div>1개</div>
          </div>
          <div className="justify-between flex-row flex">
            <div>환불 완료</div>
            <div>0,000원</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default BillingHistory;
