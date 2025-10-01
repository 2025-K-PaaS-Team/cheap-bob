import { useState } from "react";

const RegisterPackageDesc = () => {
  const [value, setValue] = useState<string>("");

  return (
    <div className="relative flex h-full mx-[20px] flex-col mt-[69px] gap-y-[11px]">
      <div className="text-[16px]">1/4</div>
      <div className="text-[24px]">
        어떤 <span className="font-bold">패키지</span>를 판매하시나요?
      </div>

      <div className="text-[14px] font-bold mt-[42px]">패키지 이름</div>
      {/* input box */}
      <input
        className="w-full h-[46px] text-center bg-[#D9D9D9] text-[16px]"
        placeholder="매장 이름을 입력해 주세요"
        value={value}
        onChange={(e) => setValue(e.target.value)}
      />

      <div className="text-[14px] font-bold mt-[29px]">패키지 설정</div>
      <div className="text-[14px]">
        패키지에 포함될 수 있는 메뉴를 설명해 주세요.
      </div>
      {/* input box */}
      <input
        className="w-full h-[100px] text-center bg-[#D9D9D9] text-[16px]"
        placeholder="매장 설명을 입력해 주세요"
        value={value}
        onChange={(e) => setValue(e.target.value)}
      />
    </div>
  );
};

export default RegisterPackageDesc;
