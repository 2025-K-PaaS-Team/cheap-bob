import { CommonBtn } from "@components/common";
import { useNavigate } from "react-router-dom";

export const NoNotiBox = () => {
  const navigate = useNavigate();

  return (
    <div className="flex flex-col h-full justify-center items-center bg-custom-white">
      <img
        src="/icon/angrySalad.svg"
        alt="saladBowlIcon"
        className="pb-[26px] w-[116px]"
      />
      <div className="text-[20px] pb-[17px] font-bold">
        주문 내역이 비어있어요.
      </div>
      <div className="text-[12px] font-base pb-[46px]">
        다양한 랜덤팩을 주문하고 픽업해보세요.
      </div>
      <CommonBtn
        label="실시간 랜덤팩 보러가기"
        notBottom
        width="w-[calc(100%-40px)]"
        onClick={() => navigate("/c/stores")}
      />
    </div>
  );
};
