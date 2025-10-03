import { CommonBtn, CommonModal } from "@components/common";
import type { SellerSignupPkgProps } from "@interface";
import { createProduct } from "@services";
import { formatErrMsg } from "@utils";
import { useState } from "react";

const ConfirmPackage = ({ pageIdx, setPageIdx, pkg }: SellerSignupPkgProps) => {
  const [showModal, setShowModal] = useState<boolean>(false);
  const [modalMsg, setModalMsg] = useState("");

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
    await handleRegisterProduct();
    setPageIdx(pageIdx + 1);
  };

  const handleClickPrev = () => {
    setPageIdx(pageIdx - 1);
  };

  return (
    <div>
      <div className="mx-[37px] mt-[155px] flex flex-col gap-y-[11px]">
        <div className="text-[24px]">이렇게 설정할까요?</div>
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
        label="설정 완료"
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

export default ConfirmPackage;
