import { useState } from "react";

const RegisterPackagePrice = () => {
  const [value, setValue] = useState<string>("");
  const discountRate = ["15", "30", "40", "50"];

  return (
    <div className="relative flex h-full mx-[20px] flex-col mt-[69px] gap-y-[11px]">
      <div className="text-[16px]">3/4</div>
      <div className="text-[24px]">패키지의 가격은 얼마인가요?</div>

      <div className="text-[14px] font-bold">패지키 원가</div>
      <div className="text-[14px]">
        패키지를 구성하는 제품의 원가를 입력해 주세요.
      </div>

      {/* input box */}
      <input
        className="w-full h-[56px] text-center bg-[#D9D9D9] text-[16px] mt-[16px] mb-[40px]"
        placeholder="제품의 원가를 입력해 주세요"
        value={value}
        onChange={(e) => setValue(e.target.value)}
      />

      {/* discount rate */}
      <div className="text-[14px] font-bold">패지키 할인율</div>
      <div className="text-[14px]">패키지를 얼마나 할인할까요?</div>

      {/* input box */}
      <div className="flex flex-row items-center justify-center gap-x-[10px] mt-[16px]">
        <input
          className="w-[204px] h-[56px] text-center bg-[#D9D9D9] text-[16px]"
          placeholder="할인율을 입력해 주세요"
          value={value}
          onChange={(e) => setValue(e.target.value)}
        />
        <span className="text-[18px]">%</span>
      </div>
      {/* input assistance btn */}
      <div className="flex flex-row gap-x-[7px] mt-[11px] mb-[40px] justify-center">
        {discountRate.map((discount) => (
          <div className="w-[52px] h-[24px] flex items-center justify-center text-center text-[13px] bg-[#d9d9d9] text-[#666666] rounded-[50px]">
            {discount}%
          </div>
        ))}
      </div>

      {/* divider */}
      <hr className="border-0 bg-black/10 h-[1px]" />

      {/* sale price */}
      <div className="flex flex-row justify-between items-center mt-[34px]">
        <div className="font-bold text-[14px]">패키지 판매가</div>
        <div className="font-bold text-[20px]">(원가*할인율)</div>
      </div>
    </div>
  );
};

export default RegisterPackagePrice;
