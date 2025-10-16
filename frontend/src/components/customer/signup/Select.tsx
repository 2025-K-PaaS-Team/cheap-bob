import { CommonBtn, CommonModal, SelectedGrid } from "@components/common";
import type { SelectItem } from "@constant";
import { useState } from "react";
import { useNavigate } from "react-router";

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
  const navigate = useNavigate();
  const [showModal, setShowModal] = useState<boolean>(false);
  const [modalMsg, setModalMsg] = useState<string>("");
  const isLastPage = selectType === "nutrition";

  const handleClick = (key: string) => {
    if (selected.includes(key)) {
      setSelected(selected.filter((item) => item != key));
    } else {
      setSelected([...selected, key]);
    }
  };

  const handleSubmit = (isLastPage: boolean) => {
    const error = validate?.(selected);
    if (error) {
      setModalMsg(error);
      setShowModal(true);
      return;
    }
    if (isLastPage) {
      navigate("/c/stores");
    } else {
      onNext();
    }
  };

  return (
    <>
      <div className="flex h-full w-full justify-center items-start pt-[92px]">
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
        label={
          selectType === "nutrition"
            ? `다음 (${selected.length}/3)`
            : selectType === "allergy"
            ? "랜덤팩 고르러 가기"
            : "건너뛰기"
        }
        onClick={() => handleSubmit(isLastPage)}
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
