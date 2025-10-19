import { CommonBtn } from "@components/common";
import { useNavigate } from "react-router";

const Noti = () => {
  const isNoti = false;
  const navigate = useNavigate();

  if (!isNoti) {
    return (
      <div className="flex flex-col w-full h-full justify-center items-center">
        <img
          src="/icon/angrySalad.svg"
          alt="saladBowlIcon"
          className="pb-[26px] w-[116px]"
        />
        <div className="text-[20px] pb-[17px] font-bold">
          주문내역이 비어있어요.
        </div>
        <div className="text-[12px] font-base pb-[46px]">
          다양한 랜덤팩을 주문하고 픽업해보세요.
        </div>
        <CommonBtn
          label="실시간 랜덤팩 보러가기"
          notBottom={true}
          onClick={() => navigate("/c/stores")}
        />
      </div>
    );
  }

  return <></>;
};

export default Noti;
