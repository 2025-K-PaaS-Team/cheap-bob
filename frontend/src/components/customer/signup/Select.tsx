import { CommonBtn } from "@components/common";
import type { SelectItem } from "@constant";
import { useState } from "react";

type SelectProps = {
  onNext: () => void;
  data?: SelectItem[];
  selectType?: string;
  validate?: (val: string[]) => string | null;
};

const Select = ({ onNext, data, selectType, validate }: SelectProps) => {
  const [selected, setSelected] = useState<string[]>([]);

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
      alert(error);
      return;
    }
    onNext();
  };

  return (
    <>
      <div className="flex h-full w-full justify-center items-start pt-[92px]">
        <div className="grid grid-cols-2 gap-[10px]">
          {data &&
            data.map(({ key, title, desc }) => (
              <div
                key={key}
                onClick={() => handleClick(key)}
                className={`relative rounded-[5px] p-[15px] w-[170px] cursor-pointer
                  ${
                    selected.includes(key)
                      ? "bg-[#484848] text-white"
                      : "bg-[#717171] text-white"
                  }
                  ${selectType === "nutrition" ? "h-[90px]" : "h-[65px]"}
                  `}
              >
                {selected.includes(key) && (
                  <img
                    src="/icon/checked.svg"
                    alt="checked"
                    className={`absolute z-10 left-1/2 -translate-x-1/2 top-6 ${
                      selectType === "nutrition" ? "top-6" : "top-[13px]"
                    }`}
                  />
                )}
                <div className="font-semibold text-[15px]">{title}</div>
                {desc && <div className="text-[11px]">{desc}</div>}
              </div>
            ))}
        </div>
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
        onClick={handleSubmit}
      />
    </>
  );
};

export default Select;
