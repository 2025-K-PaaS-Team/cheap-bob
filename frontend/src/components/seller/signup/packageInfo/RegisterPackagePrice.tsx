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
  const { packagePrice } = validationRules;

  const handleClickNext = () => {
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
    <div className="flex flex-col mx-[20px] flex-col mt-[20px] gap-y-[40px]">
      <div className="text-main-deep font-bold bodyFont">4/5</div>
      <div className="titleFont">
        <span className="font-bold">패키지의 가격</span>은 얼마인가요?
      </div>

      <CommonPrice pkg={pkg} setPkg={setPkg} />

      <CommonBtn
        category="transparent"
        label="이전"
        onClick={() => handleClickPrev()}
        notBottom
        className="absolute left-[20px] bottom-[38px]"
        width="w-[100px]"
      />
      <CommonBtn
        category={
          validateNum(pkg.price, packagePrice.minPrice) ? "green" : "grey"
        }
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
