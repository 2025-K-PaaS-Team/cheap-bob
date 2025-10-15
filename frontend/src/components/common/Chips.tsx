import type { SelectItem } from "@constant";

interface ChipsProps {
  chips: SelectItem[];
  selected: Record<string, boolean>;
  setSelected: React.Dispatch<React.SetStateAction<Record<string, boolean>>>;
}

const Chips = ({ chips, selected, setSelected }: ChipsProps) => {
  return (
    <div className="flex flex-wrap">
      <div className="flex flex-wrap gap-[4px] items-center w-max mb-[20px]">
        {chips.map((chip, idx) => (
          <div
            className={`${
              selected[chip.key]
                ? "bg-[#222222] text-white"
                : "bg-[#f0f0f0] text-custom-black"
            } rounded-[10px] px-[10px] py-[7px] text-center text-[12px] min-h-[28px] flex items-center whitespace-nowrap`}
            key={idx}
            onClick={() =>
              setSelected((prev) => ({
                ...prev,
                [chip.key]: !prev[chip.key],
              }))
            }
          >
            {chip.title}
          </div>
        ))}
      </div>
    </div>
  );
};

export default Chips;
