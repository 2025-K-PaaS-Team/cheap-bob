import { CommonBtn, CommonModal } from "@components/common";
import { CommonPrice } from "@components/seller/common";
import type { SellerSignupPkgProps } from "@interface";
import { getRoundedPrice, validateNum, validationRules } from "@utils";
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

    if (getRoundedPrice(pkg.price, pkg.sale) < 1000 || !pkg.price) {
      setModalMsg("최소 패키지 판매가는 1000원입니다.");
      setShowModal(true);
      return;
    }

    if (!validateNum(pkg.sale, 1)) {
      setModalMsg("할인율은 1~99% 사이여야 합니다.");
      setShowModal(true);
      return;
    }

    setPageIdx(pageIdx + 1);
  };

  const handleClickPrev = () => {
    setPageIdx(pageIdx - 1);
  };

  return (
    <div className="mx-[20px] my-[20px] flex flex-col flex-1 gap-y-[40px]">
      <div className="flex flex-1 flex-col gap-y-[40px]">
        <div className="text-main-deep font-bold bodyFont">4/5</div>
        <div className="titleFont">
          <span className="font-bold">패키지의 가격</span>은 얼마인가요?
        </div>
        <CommonPrice pkg={pkg} setPkg={setPkg} />
      </div>

      <div className="grid grid-cols-3">
        <CommonBtn
          category="transparent"
          label="이전"
          onClick={() => handleClickPrev()}
          notBottom
        />
        <CommonBtn
          category={
            validateNum(pkg.price, packagePrice.minPrice) ? "green" : "grey"
          }
          label="다음"
          onClick={() => handleClickNext()}
          className="col-span-2"
          notBottom
        />
      </div>

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
