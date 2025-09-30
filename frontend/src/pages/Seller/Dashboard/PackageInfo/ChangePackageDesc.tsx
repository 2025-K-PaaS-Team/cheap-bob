import { CommonBtn } from "@components/common";
import { useState } from "react";
import { useNavigate } from "react-router";

const ChangePackageDesc = () => {
  const [value, setValue] = useState<string>("");
  const navigate = useNavigate();
  const handleSubmit = () => {
    navigate(-1);
  };

  return (
    <div className="mt-[80px] px-[20px] w-full">
      {/* question */}
      <div className="text-[24px]">
        변경할 <span className="font-bold">매장 설명</span>을 <br /> 입력해
        주세요.
      </div>
      {/* input box */}
      <input
        className="w-full h-[100px] text-center bg-[#D9D9D9] text-[16px] mt-[40px]"
        placeholder="매장 설명을 입력해 주세요"
        value={value}
        onChange={(e) => setValue(e.target.value)}
      />

      {/* 다음 */}
      <CommonBtn
        label="다음"
        onClick={handleSubmit}
        className="bg-black text-white"
      />
    </div>
  );
};

export default ChangePackageDesc;
