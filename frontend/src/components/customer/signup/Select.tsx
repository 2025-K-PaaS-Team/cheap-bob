import { CommonBtn } from "@components/common";
import type { NutritionList } from "@constant";

type SelectProps = {
  onNext: () => void;
  data: typeof NutritionList;
};

const Select = ({ onNext, data }: SelectProps) => {
  const handleSubmit = () => {
    onNext();
  };
  return (
    <>
      <div className="flex h-full w-full justify-center items-center pb-[207px]">
        <div className="grid grid-cols-2 gap-x-[10px]">
          {data &&
            Object.entries(data).map(([key, value]) => (
              <div
                key={key}
                className="bg-[#717171] rounded-[5px] text-white p-3 cursor-pointer"
              >
                <div className="font-semibold text-[15px]">{value.title}</div>
                <div className="text-[11px]">{value.desc}</div>
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
