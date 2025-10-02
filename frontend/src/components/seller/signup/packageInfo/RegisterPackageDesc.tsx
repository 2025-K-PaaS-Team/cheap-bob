import { CommonBtn, CommonModal } from "@components/common";
import type { SellerSignupPkgProps } from "@interface";
import { validateLength, validationRules } from "@utils";
import { useState } from "react";

const RegisterPackageDesc = ({
  pageIdx,
  setPageIdx,
  pkg,
  setPkg,
}: SellerSignupPkgProps) => {
  const [showModal, setShowModal] = useState<boolean>(false);
  const [modalMsg, setModalMsg] = useState("");

  const handleClickNext = () => {
    const { packageName, packageDesc } = validationRules;
    if (
      !validateLength(
        pkg.product_name,
        packageName.minLength,
        packageName.maxLength
      )
    ) {
      setModalMsg(packageName.errorMessage);
      setShowModal(true);
      return;
    }
    if (
      !validateLength(
        pkg.description,
        packageDesc.minLength,
        packageDesc.maxLength
      )
    ) {
      setModalMsg(packageDesc.errorMessage);
      setShowModal(true);
      return;
    }
    setPageIdx(pageIdx + 1);
  };

  return (
    <div className="flex h-full mx-[20px] flex-col mt-[69px] gap-y-[11px]">
      <div className="text-[16px]">1/4</div>
      <div className="text-[24px]">
        어떤 <span className="font-bold">패키지</span>를 판매하시나요?
      </div>

      <div className="text-[14px] font-bold mt-[42px]">패키지 이름</div>
      {/* input box */}
      <input
        className="w-full h-[46px] text-center bg-[#D9D9D9] text-[16px]"
        placeholder="매장 이름을 입력해 주세요"
        value={pkg.product_name}
        onChange={(e) =>
          setPkg((prev) => ({ ...prev, product_name: e.target.value }))
        }
      />

      <div className="text-[14px] font-bold mt-[29px]">패키지 설정</div>
      <div className="text-[14px]">
        패키지에 포함될 수 있는 메뉴를 설명해 주세요.
      </div>
      {/* input box */}
      <input
        className="w-full h-[100px] text-center bg-[#D9D9D9] text-[16px]"
        placeholder="매장 설명을 입력해 주세요"
        value={pkg.description}
        onChange={(e) =>
          setPkg((prev) => ({ ...prev, description: e.target.value }))
        }
      />

      <CommonBtn
        category="black"
        label="다음"
        onClick={() => handleClickNext()}
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

export default RegisterPackageDesc;
