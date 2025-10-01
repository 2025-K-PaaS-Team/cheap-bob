import { CommonBtn } from "@components/common";
import { useNavigate } from "react-router";

const ChangePickupTime = () => {
  const navigate = useNavigate();
  const handleSubmit = () => {
    navigate(-1);
  };

  return (
    <div className="flex flex-col gap-y-[10px] mx-[20px]">
      {/* pickup time */}
      <div className="text-[14px] font-bold">픽업 시간</div>
      <div className="text-[14px]">
        마감 세일을 시작할 시간을 입력해 주세요.
      </div>
      <div className="text-center w-full justify-center">
        {/* before time */}
        <div className="flex flex-row text-[20px] justify-center items-center gap-x-[10px]">
          <div className="bg-[#d9d9d9] rounded-[8px] w-[50px] h-[44px] flex items-center justify-center">
            2
          </div>
          <div>시</div>
          <div className="bg-[#d9d9d9] rounded-[8px] w-[50px] h-[44px] flex items-center justify-center">
            30
          </div>
          <div>분 전부터</div>
        </div>
        <div className="text-[14px] mt-[10px]">
          19시부터 사용자들은 매장에 방문하여 <br /> 패키지를 픽업할 수
          있습니다.
        </div>
      </div>

      {/* after time */}
      <div className="text-[14px] font-bold mt-[40px]">픽업 마감 시간</div>
      <div className="text-[14px]">픽업을 마감할 시간을 입력해 주세요.</div>
      <div className="text-center w-full justify-center">
        {/* before time */}
        <div className="flex flex-row text-[20px] justify-center items-center gap-x-[10px]">
          <div className="bg-[#d9d9d9] rounded-[8px] w-[50px] h-[44px] flex items-center justify-center">
            2
          </div>
          <div>시</div>
          <div className="bg-[#d9d9d9] rounded-[8px] w-[50px] h-[44px] flex items-center justify-center">
            30
          </div>
          <div>분 전부터</div>
        </div>
        <div className="text-[14px] mt-[10px]">
          19시부터 사용자들은 매장에 방문하여 <br /> 패키지를 픽업할 수
          있습니다.
        </div>
      </div>

      {/* notice */}
      <div className="absolute bottom-30 w-[350px] left-1/2 -translate-x-1/2 bg-[#d9d9d9] rounded-[8px] h-[57px] px-[10px] flex items-center">
        변경시 다음 영업일부터 적용됩니다.
      </div>

      {/* btn */}
      <CommonBtn
        label="다음"
        onClick={handleSubmit}
        className="bg-black text-white"
      />
    </div>
  );
};

export default ChangePickupTime;
