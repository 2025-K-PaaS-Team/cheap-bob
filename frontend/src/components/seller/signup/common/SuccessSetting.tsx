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
    <div className="min-h-screen mx-[37px] justify-center items-center flex flex-col gap-y-[11px]">
      <div className="titleFont">
        {label(pageIdx)} 정보 설정을 완료했습니다!
      </div>

      <CommonBtn
        category="green"
        label="확인"
        onClick={() => handleClickNext()}
      />
    </div>
  );
};

export default SuccessSetting;
