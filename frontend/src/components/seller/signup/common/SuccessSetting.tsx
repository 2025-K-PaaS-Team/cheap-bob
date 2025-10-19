import { CommonBtn } from "@components/common";
import type { SellerSignupProps } from "@interface";
import { useNavigate } from "react-router";

const SuccessSetting = ({ pageIdx, setPageIdx }: SellerSignupProps) => {
  const navigate = useNavigate();
  const handleClickNext = () => {
    if (pageIdx < 11) {
      setPageIdx(pageIdx + 1);
    } else {
      navigate("/s/dashboard");
    }
  };

  const label = (pageIdx: number): string => {
    if (pageIdx < 7) {
      return "매장";
    } else if (pageIdx < 11) {
      return "영업";
    } else {
      return "패키지";
    }
  };

  return (
    <div className="min-h-screen mx-auto justify-center items-center flex flex-col gap-y-[40px]">
      <img src="/icon/happySalad.svg" alt="happySaldIcon" width="116px" />
      <div className="titleFont font-bold">
        {label(pageIdx)} 정보 등록 완료!
      </div>
      {/* ck box */}
      <div className="flex flex-col bodyFont rounded bg-custom-white min-w-[239px] gap-y-[20px] py-[20px] justify-center items-center">
        <div className="flex flex-row gap-x-[10px]">
          <input type="checkbox" checked={pageIdx > 5 ? true : false} />
          <div>매장 정보 등록</div>
        </div>
        <div className="flex flex-row gap-x-[10px]">
          <input type="checkbox" checked={pageIdx > 11 ? true : false} />
          <div>운영 정보 등록</div>
        </div>
        <div className="flex flex-row gap-x-[10px]">
          <input type="checkbox" checked={pageIdx > 11 ? true : false} />
          <div>패키지 등록</div>
        </div>
      </div>

      <CommonBtn
        category="green"
        label="다음"
        onClick={() => handleClickNext()}
      />
    </div>
  );
};

export default SuccessSetting;
