import { CommonBtn, CommonModal } from "@components/common";
import { PostalCode } from "@components/seller/dashboard";
import type { SellerSignupProps } from "@interface";
import { useSignupStore } from "@store";
import { validationRules } from "@utils";
import { useState } from "react";

const RegisterAddr = ({ pageIdx, setPageIdx }: SellerSignupProps) => {
  const { form } = useSignupStore();
  const [showModal, setShowModal] = useState<boolean>(false);
  const [modalMsg, setModalMsg] = useState("");

  const handleClickNext = () => {
    const { storeAddr } = validationRules;
    if (!form.address_info.address || !form.address_info.postal_code) {
      setModalMsg(storeAddr.errorMessage);
      setShowModal(true);
      return;
    }

    if (!form.address_info.detail_address?.trim()) {
      setModalMsg("상세 주소를 입력해 주세요.");
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
      <div className="titleFont">
        <span className="font-bold">매장 위치</span>를 알려주세요.
      </div>

      {/* postal code */}
      <PostalCode
        form={form.address_info}
        setForm={(addrForm) => {
          useSignupStore.getState().setForm((prev) => ({
            address_info: {
              ...prev.address_info,
              ...(typeof addrForm === "function"
                ? addrForm(prev.address_info)
                : addrForm),
            },
          }));
        }}
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

export default RegisterAddr;
