import { CommonBtn, CommonModal } from "@components/common";
import type { SellerSignupProps } from "@interface";
import { useSignupStore } from "@store";
import { validateLength, validationRules } from "@utils";
import { useState } from "react";

const RegisterName = ({ pageIdx, setPageIdx }: SellerSignupProps) => {
  const { form, setForm } = useSignupStore();
  const [showModal, setShowModal] = useState<boolean>(false);
  const [modalMsg, setModalMsg] = useState("");

  const handleClickNext = () => {
    const { storeName } = validationRules;
    if (
      !validateLength(form.store_name, storeName.minLength, storeName.maxLength)
    ) {
      setModalMsg(storeName.errorMessage);
      setShowModal(true);
      return;
    }
    setPageIdx(pageIdx + 1);
  };

  return (
    <div className="mx-[20px] mt-[69px] flex flex-col gap-y-[11px]">
      <div className="text-[16px]">1/4</div>
      <div className="text-[24px]">
        <span className="font-bold">매장 이름</span>을 <br />
        입력해 주세요.
      </div>

      {/* input box */}
      <input
        className="w-full h-[46px] text-center bg-custom-white text-[16px] mt-[40px]"
        placeholder="매장 이름을 입력해 주세요"
        value={form.store_name}
        onChange={(e) => setForm({ store_name: e.target.value })}
      />

      <CommonBtn
        category="green"
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

export default RegisterName;
