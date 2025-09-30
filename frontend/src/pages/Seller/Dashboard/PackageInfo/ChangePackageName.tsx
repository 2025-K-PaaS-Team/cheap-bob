import { CommonBtn } from "@components/common";
import { useState } from "react";
import { useNavigate } from "react-router";

const ChangePackageName = ({}) => {
  const [value, setValue] = useState<string>("");
  const navigate = useNavigate();
  const handleSubmit = () => {
    navigate(-1);
  };

  return (
    <div className="mt-[80px] px-[20px] w-full">
      {/* question */}
      <div className="text-[24px]">
        변경할 <span className="font-bold">패키지의 이름</span>을 <br /> 입력해
        주세요.
      </div>
      {/* input box */}
      <input
        className="w-full h-[46px] text-center bg-[#D9D9D9] text-[16px] mt-[40px]"
        placeholder="패키지의 이름을 입력해 주세요"
        value={value}
        onChange={(e) => setValue(e.target.value)}
      />

      {/* save */}
      <CommonBtn
        label="저장"
        onClick={handleSubmit}
        className="bg-black text-white"
      />
    </div>
  );
};

export default ChangePackageName;
