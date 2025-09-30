import type { SelectItem } from "@constant";

type SelectGridProps = {
  data: SelectItem[];
  selected: string[];
  onClick: (key: string) => void;
  selectType?: string;
};

const SelectGrid = ({
  data,
  selected,
  onClick,
  selectType,
}: SelectGridProps) => {
  return (
    <div className="grid grid-cols-2 gap-[10px]">
      {data.map(({ key, title, desc }) => (
        <div
          key={key}
          onClick={() => onClick(key)}
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
              className={`absolute z-10 left-1/2 -translate-x-1/2 ${
                selectType === "nutrition" ? "top-6" : "top-[13px]"
              }`}
            />
          )}
          <div className="font-semibold text-[15px]">{title}</div>
          {desc && <div className="text-[11px]">{desc}</div>}
        </div>
      ))}
    </div>
  );
};

export default SelectGrid;
