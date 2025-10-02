import { CommonBtn } from "@components/common";
import type { SellerSignupProps } from "@interface";

const SuccessSetting = ({ pageIdx, setPageIdx }: SellerSignupProps) => {
  const handleClickNext = () => {
    setPageIdx(pageIdx + 1);
  };

  return (
    <div className="min-h-screen mx-[37px] justify-center items-center flex flex-col gap-y-[11px]">
      <div className="text-[24px]">매장 정보 설정을 완료했습니다!</div>

      <CommonBtn
        category="black"
        label="확인"
        onClick={() => handleClickNext()}
      />
    </div>
  );
};

export default SuccessSetting;
