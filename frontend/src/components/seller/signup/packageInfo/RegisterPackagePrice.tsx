import { CommonBtn, CommonModal } from "@components/common";
import { CommonPrice } from "@components/seller/common";
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

  return (
    <div className="flex h-full mx-[20px] flex-col mt-[69px] gap-y-[11px]">
      <div className="text-[16px]">3/4</div>
      <div className="text-[24px]">패키지의 가격은 얼마인가요?</div>

      <CommonPrice pkg={pkg} setPkg={setPkg} />

      <CommonBtn
        category="grey"
        label="이전"
        onClick={() => handleClickPrev()}
        notBottom
        className="absolute left-[20px] bottom-[38px]"
        width="w-[100px]"
      />
      <CommonBtn
        category="green"
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
          category="green"
        />
      )}
    </div>
  );
};

export default RegisterPackagePrice;
