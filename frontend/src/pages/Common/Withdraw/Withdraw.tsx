import { CommonBtn } from "@components/common";
import { useNavigate } from "react-router";

const Withdraw = () => {
  const navigate = useNavigate();

  return (
    <div className="mx-[20px] flex flex-col h-full items-center justify-center text-center text-custom-black">
      <div className="titleFont pb-[10px]">계정 탈퇴가 접수되었습니다.</div>
      <div className="bodyFont pb-[176px]">
        지금까지 서비스를 이용해주셔서 감사합니다.
      </div>
      <CommonBtn
        label="첫 화면으로"
        onClick={() => navigate("/s")}
        category="white"
        notBottom
      />
      <div className="w-full bg-[#e7e7e7] rounded hintFont py-[20px] px-[8px] mt-[40px]">
        탈퇴 처리까지는 최대 1일까지 소요될 수 있습니다.
        <br />
        <br />
        문의사항:
        <br />
        cheapbob2025@gmail.com
      </div>
    </div>
  );
};

export default Withdraw;
