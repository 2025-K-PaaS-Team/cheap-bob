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
    console.log("if error 통과");
    onNext();
  };

  return (
    <>
      <input
        type="text"
        placeholder={placeholder}
        value={value}
        onChange={(e) => setValue(e.target.value)}
        className="border border-[1px] w-[350px] h-[54px] flex items-center justify-center px-[12px] rounded mt-[45px]"
      />
      {/* 다음 */}
      <CommonBtn label="다음" onClick={handleSubmit} />

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
