import { ALL_DONG_OPTION } from "@constant";

interface DongListProps {
  dongs: string[];
  selectedDongs: Record<string, boolean>;
  onToggle: (dong: string) => void;
  maxRows: number;
}

export const DongList = ({
  dongs,
  selectedDongs,
  onToggle,
  maxRows,
}: DongListProps) => {
  const fillEmptyRows = (count: number) =>
    Array.from({ length: count }, (_, i) => (
      <div key={i} className="py-3"></div>
    ));

  return (
    <div className="flex flex-col min-w-0">
      {dongs.map((dong) => {
        const isActive = !!selectedDongs[dong];
        const isAllOn = !!selectedDongs[ALL_DONG_OPTION];
        const isDisabled = isAllOn && dong !== ALL_DONG_OPTION;

        return (
          <div
            key={dong}
            className={`flex items-center justify-between w-full h-[32px] p-[10px] ${
              isDisabled || isActive ? "text-main-deep" : "text-[#393939]"
            }`}
            onClick={() => onToggle(dong)}
          >
            <span>{dong}</span>
            {(isActive || isDisabled) && (
              <img src="/icon/check.svg" alt="check" />
            )}
          </div>
        );
      })}
      {fillEmptyRows(maxRows - dongs.length)}
    </div>
  );
};
