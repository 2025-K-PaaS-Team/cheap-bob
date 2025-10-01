import { useState } from "react";

const RegisterNum = () => {
  const [value, setValue] = useState<string>("");

  return (
    <div className="mx-[20px] mt-[69px] flex flex-col gap-y-[11px]">
      <div className="text-[16px]">4/4</div>
      <div className="text-[24px]">
        <span className="font-bold">매장 연락처</span>를 알려주세요.
      </div>
      <div className="text-[16px]">손님에게 연락이 올 수 있어요.</div>

      {/* input box */}
      <div className="mt-[40px] gap-y-[11px]">
        <div className="text-[16px]">매장 전화번호 (*필수)</div>
        <input
          className="w-full h-[46px] text-center bg-[#D9D9D9] text-[16px]"
          placeholder="매장 전화번호를 입력해 주세요"
          value={value}
          onChange={(e) => setValue(e.target.value)}
        />
      </div>

      {/* other sns */}
      <div className="mt-[39px] flex flex-col gap-y-[11px]">
        <div className="text-[20px]">다른 SNS도 있나요?</div>
        <div className="flex flex-row">
          <div className="text-[14px] w-[97px] flex items-center">홈페이지</div>
          <input
            className="w-full h-[40px] text-center bg-[#D9D9D9] text-[16px]"
            value={value}
            onChange={(e) => setValue(e.target.value)}
          />
        </div>
        <div className="flex flex-row">
          <div className="text-[14px] w-[97px] flex items-center">
            인스타그램
          </div>
          <input
            className="w-full h-[40px] text-center bg-[#D9D9D9] text-[16px]"
            value={value}
            onChange={(e) => setValue(e.target.value)}
          />
        </div>
        <div className="flex flex-row">
          <div className="text-[14px] w-[97px] flex items-center">
            X (Twitter)
          </div>
          <input
            className="w-full h-[40px] text-center bg-[#D9D9D9] text-[16px]"
            value={value}
            onChange={(e) => setValue(e.target.value)}
          />
        </div>
      </div>
    </div>
  );
};

export default RegisterNum;
