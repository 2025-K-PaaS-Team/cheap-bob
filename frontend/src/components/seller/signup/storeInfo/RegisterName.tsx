import { CommonBtn, CommonModal } from "@components/common";
import { useSignupStore } from "@store";
import { validateLength, validationRules } from "@utils";
import { useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

const RegisterName = () => {
  const { pageIdx: paramPageIdx } = useParams<{ pageIdx?: string }>();
  const pageIdx = Number(paramPageIdx) ?? 0;
  const { form, setForm } = useSignupStore();
  const [showModal, setShowModal] = useState<boolean>(false);
  const [modalMsg, setModalMsg] = useState("");
  const navigate = useNavigate();

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
    <div className="mx-[20px] my-[20px] flex flex-col flex-1 gap-y-[40px]">
      <div className="flex flex-1 flex-col gap-y-[40px]">
        <div className="text-main-deep font-bold bodyFont">1/5</div>
        <div className="titleFont">
          <span className="font-bold">매장 이름</span>을 <br />
          입력해 주세요.
        </div>
        {/* input box */}
        <input
          className="w-full h-[46px] border-b  border-[#393939] text-[16px] mt-[40px]"
          placeholder="20자 이내로 매장 이름을 입력해주세요"
          value={form.store_name}
          onChange={(e) => setForm({ store_name: e.target.value })}
        />
      </div>

      <CommonBtn
        category={form.store_name ? "green" : "grey"}
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

export default RegisterName;
