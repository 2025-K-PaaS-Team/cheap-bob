import { CommonBtn } from "@components/common";
import { useState } from "react";

type EnterProps = {
  placeholder: string;
  onNext: () => void;
};
const Enter = ({ placeholder, onNext }: EnterProps) => {
  const [value, setValue] = useState<string>("");
  const handleSubmit = () => {
    if (value.length > 7) {
      alert("7자 이내로 닉네임을 입력해주세요");
      return;
    }
    onNext();
  };

  return (
    <>
      <input
        type="text"
        placeholder={placeholder}
        value={value}
        onChange={(e) => setValue(e.target.value)}
        className="border border-[1px] w-[350px] h-[54px] flex items-center justify-center px-[12px] rounded-[10px] mt-[45px]"
      />
      {/* 다음 */}
      <CommonBtn label="다음" onClick={handleSubmit} />
    </>
  );
};

export default Enter;
