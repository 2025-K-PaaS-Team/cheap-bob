import { CommonBtn, CommonModal } from "@components/common";
import { CommonOpTime } from "@components/seller/common";
import type { SellerSignupProps } from "@interface";
import { useSignupStore } from "@store";
import { validateLength, validationRules } from "@utils";
import { useEffect, useState } from "react";

const RegisterOpTime = ({ pageIdx, setPageIdx }: SellerSignupProps) => {
  const { form, setForm } = useSignupStore();
  const [showModal, setShowModal] = useState<boolean>(false);
  const [modalMsg, setModalMsg] = useState("");

  useEffect(() => {
    console.log(form);
  }, [form]);

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
    <div className="flex mx-[20px] flex-col my-[20px] gap-y-[20px]">
      <div className="flex flex-1 flex-col gap-y-[40px]">
        {/* progress */}
        <div className="text-main-deep font-bold bodyFont">1/2</div>
        {/* opertation Time */}
        <CommonOpTime
          form={form.operation_times}
          setForm={(times) =>
            setForm((prev) => ({
              ...prev,
              operation_times: times,
            }))
          }
        />
      </div>

      {/* next */}
      <CommonBtn
        category="green"
        label="다음"
        notBottom
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

export default RegisterOpTime;
