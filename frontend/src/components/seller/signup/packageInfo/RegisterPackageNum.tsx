import { CommonBtn, CommonModal } from "@components/common";
import { CommonPkgNum } from "@components/seller/common";
import type { SellerSignupPkgProps } from "@interface";
import { createProduct } from "@services";
import { formatErrMsg, validateNum, validationRules } from "@utils";
import { useState } from "react";

const RegisterPackageNum = ({
  pageIdx,
  setPageIdx,
  pkg,
  setPkg,
}: SellerSignupPkgProps) => {
  const [showModal, setShowModal] = useState<boolean>(false);
  const [modalMsg, setModalMsg] = useState("");
  const { packageStock } = validationRules;

  const handleRegisterProduct = async () => {
    try {
      const res = await createProduct(pkg);
      console.log("등록 성공:", res);
    } catch (err) {
      setModalMsg(formatErrMsg(err));
      setShowModal(true);
    }
  };

  const handleClickNext = async () => {
    if (!validateNum(pkg.initial_stock, packageStock.minStock)) {
      setModalMsg(packageStock.errorMessage);
      setShowModal(true);
      return;
    }
    try {
      await handleRegisterProduct();
      setPageIdx(pageIdx + 1);
    } catch (err) {
      setModalMsg(formatErrMsg(err));
      setShowModal(true);
    }
  };

  const handleClickPrev = () => {
    setPageIdx(pageIdx - 1);
  };
  return (
    <div className="mx-[20px] my-[20px] flex flex-col flex-1 gap-y-[40px]">
      <div className="flex flex-1 flex-col gap-y-[40px]">
        <div className="text-main-deep font-bold bodyFont">5/5</div>
        {/* common pkg num */}
        <CommonPkgNum pkg={pkg} setPkg={setPkg} />
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
            validateNum(pkg.initial_stock, packageStock.minStock)
              ? "green"
              : "grey"
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

export default RegisterPackageNum;
