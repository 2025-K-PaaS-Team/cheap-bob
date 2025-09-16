import { CommonBtn } from "@components/common";
import type { SelectItem } from "@constant";
import { useState } from "react";

type SelectProps = {
  onNext: () => void;
  data?: SelectItem[];
};

const Select = ({ onNext, data }: SelectProps) => {
  const [selected, setSelected] = useState<string>("");
  const handleSubmit = () => {
    if (!selected) {
      alert("항목을 선택해주세요");
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
                onClick={() => setSelected(key)}
                className={`relative rounded-[5px] p-[15px] h-[90px] w-[170px] cursor-pointer
                  ${
                    selected === key
                      ? "bg-[#484848] text-white"
                      : "bg-[#717171] text-white"
                  }`}
              >
                {selected === key && (
                  <img
                    src="/icon/checked.svg"
                    alt="checked"
                    className="absolute z-10 left-1/2 -translate-x-1/2 top-6"
                  />
                )}
                <div className="font-semibold text-[15px]">{title}</div>
                {desc && <div className="text-[11px]">{desc}</div>}
              </div>
            ))}
        </div>
      </div>
      {/* 다음 */}
      <CommonBtn label="다음" onClick={handleSubmit} />
    </>
  );
};

export default Select;
