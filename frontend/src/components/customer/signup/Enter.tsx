import { CommonBtn, CommonModal } from "@components/common";
import { useState } from "react";

type EnterProps = {
  placeholder: string;
  onNext: () => void;
  setValue: React.Dispatch<React.SetStateAction<string>>;
  value: string;
  validate: (val: string) => string | null;
  inputType?: "text" | "phone";
};

const Enter = ({
  placeholder,
  onNext,
  setValue,
  value,
  validate,
  inputType = "text",
}: EnterProps) => {
  const [showModal, setShowModal] = useState<boolean>(false);
  const [modalMsg, setModalMsg] = useState<string>("");

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    let val = e.target.value;

    if (inputType === "phone") {
      val = val.replace(/\D/g, "");
      if (val.length > 3 && val.length <= 7) {
        val = val.replace(/(\d{3})(\d+)/, "$1-$2");
      } else if (val.length > 7) {
        val = val.replace(/(\d{3})(\d{4})(\d+)/, "$1-$2-$3");
      }
    }

    setValue(val);
  };

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
      <div className="flex flex-1 justify-center mx-[20px]">
        <input
          type="text"
          placeholder={placeholder}
          value={value}
          onChange={handleChange}
          className="w-full h-[46px] border-b  border-[#393939] text-[16px] mt-[40px]"
        />
      </div>

      {/* 다음 */}
      <div className="mx-[20px]">
        <CommonBtn
          label="다음"
          notBottom
          onClick={handleSubmit}
          category={!validate(value) ? "green" : "grey"}
        />
      </div>

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
