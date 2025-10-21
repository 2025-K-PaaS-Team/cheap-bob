import type { SelectItem } from "@constant";

interface ChipsProps {
  chips: SelectItem[];
  selected: Record<string, boolean>;
  setSelected: React.Dispatch<React.SetStateAction<Record<string, boolean>>>;
}

const Chips = ({ chips, selected, setSelected }: ChipsProps) => {
  const chipsWithAll = [{ key: "all", title: "전체" }, ...chips];

  const handleClick = (chipKey: string) => {
    setSelected((prev) => {
      // 전체 칩 클릭 시
      if (chipKey === "all") {
        return {
          ...prev,
          all: !prev.all,
        };
      }
      // 일반 칩 클릭 시
      return {
        ...prev,
        [chipKey]: !prev[chipKey],
        all: false,
      };
    });
  };

  const isNoneSelected =
    !Object.values(selected).some((v) => v) || selected["all"];

  return (
    <div className="flex flex-wrap">
      <div className="flex overflow-x-auto gap-[4px] items-center w-max my-[20px]">
        {chipsWithAll.map((chip, idx) => {
          const isActive =
            chip.key === "all" ? isNoneSelected : selected[chip.key];

          return (
            <div
              key={idx}
              className={`${
                isActive
                  ? "bg-main-pale text-main-deep border border-main-deep"
                  : "text-custom-black"
              } rounded px-[10px] py-[7px] text-center tagFont min-h-[28px] flex items-center whitespace-nowrap cursor-pointer`}
              onClick={() => handleClick(chip.key)}
            >
              {chip.title}
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default Chips;
