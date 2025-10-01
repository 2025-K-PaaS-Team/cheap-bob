import { useState } from "react";

const StatusBar = () => {
  const items = [
    { label: "확정 대기중", idx: 0 },
    { label: "픽업 확정", idx: 1 },
    { label: "픽업 완료/취소", idx: 2 },
  ];
  const [status, setStatus] = useState<number>(0);

  return (
    <div className="grid grid-cols-3 text-center">
      {items.map((item) => (
        <div key={item.idx} className="flex flex-col items-center">
          <div
            className="h-[64px] flex items-center"
            onClick={() => setStatus(item.idx)}
          >
            {item.label}
          </div>
          {item.idx === status ? (
            <hr className="w-full border-0 h-[3px] bg-black" />
          ) : (
            <hr className="w-full border-0 h-[3px] bg-black/20" />
          )}
        </div>
      ))}
    </div>
  );
};

export default StatusBar;
