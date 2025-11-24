const headers = ["시 · 도", "시 · 군 · 구", "동 · 읍 · 면"];

export const LocationHeader = () => (
  <div className="grid grid-cols-3 overflow-y-scroll min-h-[30px]">
    {headers.map((header, idx) => (
      <div
        key={idx}
        className={`text-center py-2 bg-[#F0F0F0] text-[11px] ${
          idx < 2 ? "border-r border-[#BFBFBF]" : ""
        }`}
      >
        {header}
      </div>
    ))}
  </div>
);
