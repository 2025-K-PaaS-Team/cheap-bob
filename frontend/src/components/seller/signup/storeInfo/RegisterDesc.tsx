import { CommonBtn, CommonModal } from "@components/common";
import { useSignupStore } from "@store";
import { validateLength, validationRules } from "@utils";
import { useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

const RegisterDesc = () => {
  const { pageIdx: paramPageIdx } = useParams<{ pageIdx?: string }>();
  const pageIdx = Number(paramPageIdx) ?? 0;
  const navigate = useNavigate();
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
    navigate(`/s/signup/${pageIdx + 1}`);
  };

  const handleClickPrev = () => {
    navigate(`/s/signup/${pageIdx - 1}`);
  };

  return (
    <div className="mx-[20px] my-[20px] flex flex-col flex-1 gap-y-[40px]">
      <div className="flex flex-1 flex-col gap-y-[40px]">
        <div className="text-main-deep font-bold bodyFont">2/5</div>
        <div className="titleFont">
          <span className="font-bold">매장</span>에 대해{" "}
          <span className="font-bold">소개</span>해 주세요.
        </div>

        {/* input box */}
        <textarea
          className="w-full h-[145px] rounded border border-[#E7E7E7] text-[16px] mt-[40px] p-[8px]"
          placeholder="텍스트를 입력하세요"
          value={form.store_introduction}
          onChange={(e) => setForm({ store_introduction: e.target.value })}
        />
      </div>

      <div className="grid grid-cols-3">
        <CommonBtn
          category="transparent"
          label="이전"
          onClick={() => handleClickPrev()}
          notBottom
        />
        <CommonBtn
          category={form.store_introduction ? "green" : "grey"}
          label="다음"
          onClick={() => handleClickNext()}
          notBottom
          className="col-span-2"
        />
      </div>

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

export default RegisterDesc;
