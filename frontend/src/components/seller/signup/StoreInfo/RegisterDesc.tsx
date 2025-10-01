import { useState } from "react";

const RegisterName = () => {
  const [value, setValue] = useState<string>("");

  return (
    <div className="mx-[20px] mt-[69px] flex flex-col gap-y-[11px]">
      <div className="text-[16px]">2/4</div>
      <div className="text-[24px]">
        <span className="font-bold">매장</span>에 대해{" "}
        <span className="font-bold">소개</span>해 주세요.
      </div>

      {/* input box */}
      <input
        className="w-full h-[46px] text-center bg-[#D9D9D9] text-[16px] mt-[40px]"
        placeholder="매장 이름을 입력해 주세요"
        value={value}
        onChange={(e) => setValue(e.target.value)}
      />
    </div>
  );
};

export default RegisterName;
