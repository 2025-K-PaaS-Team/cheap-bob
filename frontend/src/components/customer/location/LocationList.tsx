interface LocationListProps {
  items: string[];
  selected: string | null;
  onSelect: (val: string) => void;
  maxRows: number;
}

export const LocationList = ({
  items,
  selected,
  onSelect,
  maxRows,
}: LocationListProps) => {
  const fillEmptyRows = (count: number) =>
    Array.from({ length: count }, (_, i) => (
      <div key={i} className="py-3"></div>
    ));

  return (
    <div className="flex flex-col border-r border-[#BFBFBF]">
      {items.map((item) => (
        <div
          key={item}
          className={`flex items-center cursor-pointer w-full h-[32px] p-[10px] ${
            selected === item
              ? "bg-main-deep font-bold text-white"
              : "text-[#393939]"
          }`}
          onClick={() => onSelect(item)}
        >
          {item}
        </div>
      ))}
      {fillEmptyRows(maxRows - items.length)}
    </div>
  );
};
