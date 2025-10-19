type SelectGridProps<T extends string> = {
  data: { key: T; title: string; desc?: string }[];
  selected: string[];
  onClick: (key: T) => void;
  selectType?: string;
};

const SelectGrid = <T extends string>({
  data,
  selected,
  onClick,
  selectType,
}: SelectGridProps<T>) => {
  return (
    <div className="grid grid-cols-2 w-full gap-[10px]">
      {data.map(({ key, title, desc }) => (
        <div
          key={key}
          onClick={() => onClick(key)}
          className={`relative rounded-[5px] p-[10px] cursor-pointer shadow border
            ${
              selected.includes(key)
                ? "bg-main-pale text-main-deep border-main-deep"
                : "bg-white text-custom-black"
            }
            ${selectType === "nutrition" ? "h-[90px]" : "h-[65px]"}
          `}
        >
          <div className="font-bold bodyFont">{title}</div>
          {desc && <div className="hintFont">{desc}</div>}
        </div>
      ))}
    </div>
  );
};

export default SelectGrid;
