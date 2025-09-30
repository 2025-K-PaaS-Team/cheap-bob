import { CommonBtn } from "@components/common";
import { PostalCode } from "@components/seller/dashboard";
import { useNavigate } from "react-router";

const ChangeStoreAddr = () => {
  const navigate = useNavigate();
  const handleSubmit = () => {
    navigate(-1);
  };

  return (
    <div className="mt-[80px] px-[20px] w-full">
      {/* question */}
      <div className="text-[24px]">
        변경할 <span className="font-bold">매장 주소</span>를 <br /> 입력해
        주세요.
      </div>
      {/* postal code */}
      <PostalCode />

      {/* 다음 */}
      <CommonBtn
        label="다음"
        onClick={handleSubmit}
        className="bg-black text-white"
      />
    </div>
  );
};

export default ChangeStoreAddr;
