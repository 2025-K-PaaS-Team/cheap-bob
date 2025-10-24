import CommonAgree from "@components/customer/signup/Agree";
import { useNavigate, useParams } from "react-router-dom";

const SellerAgree = () => {
  const { pageIdx: paramPageIdx } = useParams<{ pageIdx?: string }>();
  const pageIdx = Number(paramPageIdx) ?? 0;

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
      <CommonAgree onNext={() => navigate(`/s/signup/${pageIdx + 1}`)} />
    </div>
  );
};

export default SellerAgree;
