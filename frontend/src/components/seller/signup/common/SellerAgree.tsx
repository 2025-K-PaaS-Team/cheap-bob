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
    <div className="relative min-h-screen mx-[20px]">
      <div className="h-[75px] pt-[15px] grid grid-cols-3 items-center">
        {/* left */}

        <img
          src="/icon/before.svg"
          alt="beforeArrowIcon"
          onClick={handleClickBefore}
        />
      </div>
      <div className="pt-[42px] titleFont">
        서비스 이용 약관에 <br />
        동의해주세요
      </div>

      {/* common agree component */}
      <CommonAgree onNext={() => setPageIdx(pageIdx + 1)} />
    </div>
  );
};

export default SellerAgree;
