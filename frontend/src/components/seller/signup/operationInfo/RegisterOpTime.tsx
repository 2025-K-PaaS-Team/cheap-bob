import { CommonBtn, CommonModal } from "@components/common";
import { CommonOpTime } from "@components/seller/common";
import type { OperationTimeType } from "@interface";
import { useSignupStore } from "@store";
import { validateLength, validationRules } from "@utils";
import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

const RegisterOpTime = () => {
  const { pageIdx: paramPageIdx } = useParams<{ pageIdx?: string }>();
  const pageIdx = Number(paramPageIdx) ?? 0;
  const { form, setForm } = useSignupStore();
  const [showModal, setShowModal] = useState<boolean>(false);
  const [modalMsg, setModalMsg] = useState("");
  const navigate = useNavigate();

  const getValid = (ops: OperationTimeType[]) => {
    return ops.some((op) => op.is_open_enabled == true);
  };

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
    navigate(`/s/signup/${pageIdx + 1}`);
  };

  return (
    <div className="flex mx-[20px] flex-col flex-1 my-[20px] gap-y-[20px]">
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
        category={getValid(form.operation_times) ? "green" : "grey"}
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
