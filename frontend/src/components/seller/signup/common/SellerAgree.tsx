import CommonAgree from "@components/customer/signup/Agree";
import type { SellerSignupProps } from "@interface";
import { useNavigate } from "react-router";

const SellerAgree = ({ setPageIdx, pageIdx }: SellerSignupProps) => {
  const navigate = useNavigate();
  // handleClickBefore
  const handleClickBefore = () => {
    navigate(-1);
  };

  return (
    <div className="flex flex-1 flex-col h-full pb-[42px]">
      <div className="flex flex-col flex-1 gap-y-[42px] mx-[20px] titleFont">
        {/* left */}
        <img
          src="/icon/before.svg"
          alt="beforeArrowIcon"
          onClick={handleClickBefore}
          className="h-[75px]"
          width="12px"
        />

        <div className="titleFont">
          서비스 이용 약관에 <br />
          동의해주세요
        </div>
      </div>

      {/* common agree component */}
      <CommonAgree onNext={() => setPageIdx(pageIdx + 1)} />
    </div>
  );
};

export default SellerAgree;
