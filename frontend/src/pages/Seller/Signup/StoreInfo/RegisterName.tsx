import { CommonBtn } from "@components/common";
import { useState } from "react";
import { useNavigate } from "react-router";

const RegisterName = () => {
  const [value, setValue] = useState<string>("");
  const navigate = useNavigate();
  const handleSubmit = () => {
    navigate(-1);
  };

  return (
    <div className="mx-[20px] mt-[69px] flex flex-col gap-y-[11px]">
      <div className="text-[16px]">1/4</div>
      <div className="text-[24px]">
        <span className="font-bold">매장 이름</span>을 <br />
        입력해 주세요.
      </div>

      {/* input box */}
      <input
        className="w-full h-[46px] text-center bg-[#D9D9D9] text-[16px] mt-[40px]"
        placeholder="매장 이름을 입력해 주세요"
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

export default RegisterName;
