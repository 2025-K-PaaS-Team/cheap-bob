import { CommonBtn, CommonModal } from "@components/common";
import { CommonOpTime } from "@components/seller/common";
import type { SellerSignupProps } from "@interface";
import { useSignupStore } from "@store";
import { validateLength, validationRules } from "@utils";
import { useState } from "react";

const RegisterOpTime = ({ pageIdx, setPageIdx }: SellerSignupProps) => {
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
    <div className="flex mx-[20px] flex-col mt-[69px] gap-y-[11px]">
      {/* title */}
      <div className="text-[16px]">1/4</div>
      <div className="text-[24px]">
        매장의
        <span className="font-bold">오픈 시간</span>과 <br />{" "}
        <span className="font-bold">매감 시간</span>을 알려주세요.
      </div>

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

      {/* next */}
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
          onConfirmClcik={() => setShowModal(false)}
          category="black"
        />
      )}
    </div>
  );
};

export default RegisterOpTime;
