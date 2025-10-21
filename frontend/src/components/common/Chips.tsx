import { useEffect } from "react";
import type { SelectItem } from "@constant";

interface ChipsProps {
  chips: SelectItem[];
  selected: Record<string, boolean>;
  setSelected: React.Dispatch<React.SetStateAction<Record<string, boolean>>>;
}

const Chips = ({ chips, selected, setSelected }: ChipsProps) => {
  const chipsWithAll = [{ key: "all", title: "전체" }, ...chips];

  const makeInitState = () =>
    Object.fromEntries(
      ["all", ...chips.map((c) => c.key)].map((k) => [k, k === "all"])
    ) as Record<string, boolean>;

  useEffect(() => {
    const keys = new Set(["all", ...chips.map((c) => c.key)]);
    const hasAllKeys = Array.from(keys).every((k) => k in selected);
    if (!hasAllKeys) {
      setSelected(makeInitState());
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [chips]);

  const makeResetFalse = () =>
    Object.fromEntries(
      ["all", ...chips.map((c) => c.key)].map((k) => [k, false])
    ) as Record<string, boolean>;

  const handleClick = (chipKey: string) => {
    setSelected((prev) => {
      if (chipKey === "all") {
        const reset = makeResetFalse();
        return { ...reset, all: true };
      }

      // 개별 토글 → 전체 해제
      const next = {
        ...prev,
        [chipKey]: !prev[chipKey],
        all: false,
      };

      // 개별이 모두 false면 → 전체 복귀
      const anyOn = chips.some((c) => next[c.key]);
      if (!anyOn) {
        const reset = makeResetFalse();
        return { ...reset, all: true };
      }

      return next;
    });
  };

  const isAll = !!selected["all"];

  return (
    <div className="flex flex-wrap">
      <div className="flex overflow-x-auto gap-[4px] items-center w-max my-[20px]">
        {chipsWithAll.map((chip) => {
          const active = chip.key === "all" ? isAll : !!selected[chip.key];

          return (
            <div
              key={chip.key}
              className={`${
                active
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
