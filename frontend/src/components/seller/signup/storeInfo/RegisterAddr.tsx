import { CommonBtn, CommonModal } from "@components/common";
import { PostalCode } from "@components/seller/dashboard";
import type { AddressInfoType, SellerSignupProps } from "@interface";
import { useSignupStore } from "@store";
import { validateLength, validationRules } from "@utils";
import { useState } from "react";

const RegisterAddr = ({ pageIdx, setPageIdx }: SellerSignupProps) => {
  const { form, setForm } = useSignupStore();
  const [showModal, setShowModal] = useState<boolean>(false);
  const [modalMsg, setModalMsg] = useState("");

  const handleClickNext = () => {
    const { storeDesc } = validationRules;
    if (
      !validateLength(
        form.store_introduction,
        storeDesc.minLength,
        storeDesc.maxLength
      )
    ) {
      setModalMsg(storeDesc.errorMessage);
      setShowModal(true);
      return;
    }
    setPageIdx(pageIdx + 1);
  };

  const handleClickPrev = () => {
    setPageIdx(pageIdx - 1);
  };

  return (
    <div className="mx-[20px] mt-[69px] flex flex-col gap-y-[11px]">
      <div className="text-[16px]">3/4</div>
      <div className="text-[24px]">
        <span className="font-bold">매장 위치</span>를 알려주세요.
      </div>

      {/* postal code */}
      <PostalCode
        form={form.address_InfoType}
        setForm={(addrForm: Partial<AddressInfoType>) =>
          setForm({
            address_InfoType: { ...form.address_InfoType, ...addrForm },
          })
        }
      />

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
          onConfirmClcik={() => setShowModal(false)}
          category="black"
        />
      )}
    </div>
  );
};

export default RegisterAddr;
