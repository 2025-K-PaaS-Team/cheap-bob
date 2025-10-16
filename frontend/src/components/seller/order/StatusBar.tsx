interface StatusBarProps {
  status: string;
  setStatus: (status: string) => void;
}

const StatusBar = ({ status, setStatus }: StatusBarProps) => {
  const items = [
    { label: "확정 대기중", status: "reservation" },
    { label: "픽업 확정", status: "accept" },
    { label: "픽업 완료/취소", status: "others" },
  ];

  return (
    <div className="grid grid-cols-3 text-center">
      {items.map((item) => (
        <div key={item.status} className="flex flex-col items-center">
          <div
            className="h-[64px] flex items-center"
            onClick={() => setStatus(item.status)}
          >
            {item.label}
          </div>
          {item.status === status ? (
            <hr className="w-full border-0 h-[3px] bg-main-deep" />
          ) : (
            <hr className="w-full border-0 h-[3px] bg-white" />
          )}
        </div>
      ))}
    </div>
  );
};

export default StatusBar;
