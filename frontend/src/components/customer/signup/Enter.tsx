import { CommonBtn, CommonModal } from "@components/common";
import { useState } from "react";

type EnterProps = {
  placeholder: string;
  onNext: () => void;
  setValue: React.Dispatch<React.SetStateAction<string>>;
  value: string;
  validate: (val: string) => string | null;
};
const Enter = ({
  placeholder,
  onNext,
  setValue,
  value,
  validate,
}: EnterProps) => {
  const [showModal, setShowModal] = useState<boolean>(false);
  const [modalMsg, setModalMsg] = useState<string>("");

  const handleSubmit = () => {
    const error = validate(value);
    if (error) {
      setModalMsg(error);
      setShowModal(true);
      return;
    }
    onNext();
  };

  return (
    <>
      <input
        type="text"
        placeholder={placeholder}
        value={value}
        onChange={(e) => setValue(e.target.value)}
        className="w-full h-[46px] border-b  border-[#393939] text-[16px] mt-[40px]"
      />
      {/* 다음 */}
      <CommonBtn
        label="다음"
        onClick={handleSubmit}
        category={!validate(value) ? "green" : "grey"}
      />

      {showModal && (
        <CommonModal
          desc={modalMsg}
          confirmLabel="확인"
          onConfirmClick={() => setShowModal(false)}
          category="green"
        />
      )}
    </>
  );
};

export default Enter;
