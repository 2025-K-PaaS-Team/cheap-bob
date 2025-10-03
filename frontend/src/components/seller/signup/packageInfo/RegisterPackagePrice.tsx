import { CommonBtn, CommonModal } from "@components/common";
import type { SellerSignupPkgProps } from "@interface";
import { validateNum, validationRules } from "@utils";
import { useState } from "react";

const RegisterPackagePrice = ({
  pageIdx,
  setPageIdx,
  pkg,
  setPkg,
}: SellerSignupPkgProps) => {
  const [showModal, setShowModal] = useState<boolean>(false);
  const [modalMsg, setModalMsg] = useState("");

  const handleClickNext = () => {
    const { packagePrice } = validationRules;
    if (!validateNum(pkg.price, packagePrice.minPrice)) {
      setModalMsg(packagePrice.errorMessage);
      setShowModal(true);
      return;
    }
    setPageIdx(pageIdx + 1);
  };

  const handleClickPrev = () => {
    setPageIdx(pageIdx - 1);
  };
  const discountRate = ["15", "30", "40", "50"];

  return (
    <div className="flex h-full mx-[20px] flex-col mt-[69px] gap-y-[11px]">
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
        value={pkg.price}
        onChange={(e) =>
          setPkg((prev) => ({ ...prev, price: Number(e.target.value) }))
        }
      />

      {/* discount rate */}
      <div className="text-[14px] font-bold">패지키 할인율</div>
      <div className="text-[14px]">패키지를 얼마나 할인할까요?</div>

      {/* input box */}
      <div className="flex flex-row items-center justify-center gap-x-[10px] mt-[16px]">
        <input
          className="w-[204px] h-[56px] text-center bg-[#D9D9D9] text-[16px]"
          placeholder="할인율을 입력해 주세요"
          value={pkg.sale}
          onChange={(e) =>
            setPkg((prev) => ({ ...prev, sale: Number(e.target.value) }))
          }
        />
        <span className="text-[18px]">%</span>
      </div>
      {/* input assistance btn */}
      <div className="flex flex-row gap-x-[7px] mt-[11px] mb-[40px] justify-center">
        {discountRate.map((discount) => {
          const discountNum = Number(discount);
          const isSelected = pkg.sale === discountNum;

          return (
            <div
              key={discount}
              className={`w-[52px] h-[24px] flex items-center justify-center text-center text-[13px] rounded-[50px] cursor-pointer
          ${isSelected ? "bg-black text-white" : "bg-[#d9d9d9] text-[#666666]"}
        `}
              onClick={() => setPkg((prev) => ({ ...prev, sale: discountNum }))}
            >
              {discount}%
            </div>
          );
        })}
      </div>

      {/* divider */}
      <hr className="border-0 bg-black/10 h-[1px]" />

      {/* sale price */}
      <div className="flex flex-row justify-between items-center mt-[34px]">
        <div className="font-bold text-[14px]">패키지 판매가</div>
        <div className="font-bold text-[20px]">
          {pkg.price * pkg.sale * 0.01} 원
        </div>
      </div>

      <CommonBtn
        category="grey"
        label="이전"
        onClick={() => handleClickPrev()}
        notBottom
        className="absolute left-[20px] bottom-[38px]"
        width="w-[100px]"
      />
      <CommonBtn
        category="black"
        label="다음"
        onClick={() => handleClickNext()}
        notBottom
        className="absolute right-[20px] bottom-[38px]"
        width="w-[250px]"
      />

      {/* show modal */}
      {showModal && (
        <CommonModal
          desc={modalMsg}
          confirmLabel="확인"
          onConfirmClick={() => setShowModal(false)}
          category="black"
        />
      )}
    </div>
  );
};

export default RegisterPackagePrice;
