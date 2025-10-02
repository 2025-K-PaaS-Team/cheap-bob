import { CommonBtn } from "@components/common";
import type { SellerSignupProps } from "@interface";

const ConfirmSetting = ({ pageIdx, setPageIdx }: SellerSignupProps) => {
  const handleClickNext = () => {
    setPageIdx(pageIdx + 1);
  };

  const handleClickPrev = () => {
    setPageIdx(pageIdx - 1);
  };

  return (
    <div>
      <div className="mx-[37px] mt-[155px] flex flex-col gap-y-[11px]">
        <div className="text-[24px]">이렇게 설정할까요?</div>
      </div>

      <CommonBtn
        category="grey"
        label="이전"
        onClick={() => handleClickPrev()}
        notBottom
        className="absolute left-[20px] bottom-[38px]"
        width="w-[100px]"
      />
      <CommonBtn
        category="black"
        label="설정 완료"
        onClick={() => handleClickNext()}
        notBottom
        className="absolute right-[20px] bottom-[38px]"
        width="w-[250px]"
      />
    </div>
  );
};

export default ConfirmSetting;
