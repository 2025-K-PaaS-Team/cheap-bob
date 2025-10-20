import { CommonBtn, CommonModal, SelectedGrid } from "@components/common";
import type { SelectItem } from "@constant";
import { useState } from "react";

type SelectProps = {
  onNext: () => void;
  data?: SelectItem[];
  selected: string[];
  setSelected: React.Dispatch<React.SetStateAction<string[]>>;
  selectType?: string;
  validate?: (val: string[]) => string | null;
};

const Select = ({
  onNext,
  data,
  selectType,
  validate,
  selected,
  setSelected,
}: SelectProps) => {
  const [showModal, setShowModal] = useState<boolean>(false);
  const [modalMsg, setModalMsg] = useState<string>("");

  const handleClick = (key: string) => {
    if (selected.includes(key)) {
      setSelected(selected.filter((item) => item != key));
    } else {
      setSelected([...selected, key]);
    }
  };

  const handleSubmit = () => {
    const error = validate?.(selected);
    if (error) {
      setModalMsg(error);
      setShowModal(true);
      return;
    }
    onNext();
  };

  return (
    <>
      <div className="flex py-[25px] justify-center items-center">
        {data && (
          <SelectedGrid
            data={data}
            selected={selected}
            selectType={selectType}
            onClick={handleClick}
          />
        )}
      </div>
      {/* 다음 */}

      <CommonBtn
        category={!validate?.(selected) ? "green" : "grey"}
        label={
          selectType === "nutrition"
            ? `다음 (${selected.length}/3)`
            : selectType === "allergy"
            ? "랜덤팩 고르러 가기"
            : "건너뛰기"
        }
        onClick={() => handleSubmit()}
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

export default Select;
