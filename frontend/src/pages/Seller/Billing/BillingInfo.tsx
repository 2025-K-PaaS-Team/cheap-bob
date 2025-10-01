import { useNavigate } from "react-router";

const BillingInfo = () => {
  const navigate = useNavigate();

  return (
    <div>
      <div className="text-[24px] mx-[37px]">
        <div>이번 주 수익</div>
        <div>00,000원</div>
        <div
          className="mt-[10px] text-black/80 text-[18px]"
          onClick={() => navigate("history")}
        >
          정산 내역 보기 &gt;
        </div>

        <hr className="h-[1px] border-0 bg-black/20 mb-[44px] mt-[369px]" />

        {/* change billing info */}
        <div
          className="text-[16px] font-bold py-[20px] flex flex-row justify-between"
          onClick={() => navigate("change")}
        >
          <div>정산 정보 변경</div>
          <div>&gt;</div>
        </div>
        {/* help */}
        <div className="text-[16px] font-bold py-[20px] flex flex-row justify-between">
          <div>도움말</div>
          <div>&gt;</div>
        </div>
      </div>
    </div>
  );
};

export default BillingInfo;
