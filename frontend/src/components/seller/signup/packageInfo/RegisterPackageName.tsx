import { CommonBtn, CommonModal } from "@components/common";
import type { SellerSignupPkgProps } from "@interface";
import { validateLength, validationRules } from "@utils";
import { useState } from "react";

const RegisterPackageName = ({
  pageIdx,
  setPageIdx,
  pkg,
  setPkg,
}: SellerSignupPkgProps) => {
  const [showModal, setShowModal] = useState<boolean>(false);
  const [modalMsg, setModalMsg] = useState("");
  const { packageName } = validationRules;

  const handleClickNext = () => {
    if (
      !validateLength(
        pkg?.product_name,
        packageName.minLength,
        packageName.maxLength
      )
    ) {
      setModalMsg(packageName.errorMessage);
      setShowModal(true);
      return;
    }

    setPageIdx(pageIdx + 1);
  };

  console.log(pkg);

  return (
    <div className="flex h-full mx-[20px] flex-col mt-[20px] gap-y-[11px]">
      <div className="text-main-deep font-bold bodyFont">1/5</div>
      <div className="titleFont">
        <span className="font-bold">패키지 이름</span>을<br /> 입력해 주세요.
      </div>

      {/* input box */}
      <input
        className="w-full h-[46px] border-b  border-[#393939] hintFont mt-[40px]"
        placeholder="텍스트를 입력하세요"
        value={pkg?.product_name}
        onChange={(e) =>
          setPkg((prev) => ({ ...prev, product_name: e.target.value }))
        }
      />

      <CommonBtn
        category={
          validateLength(
            pkg?.product_name,
            packageName.minLength,
            packageName.maxLength
          )
            ? "green"
            : "grey"
        }
        label="다음"
        onClick={() => handleClickNext()}
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

export default RegisterPackageName;
