const ConfirmOp = () => {
  const shopTimes = [
    { label: "오픈", value: "09:00" },
    { label: "픽업 시작", value: "12:00" },
    { label: "픽업 마감", value: "14:00" },
    { label: "마감", value: "21:00" },
  ];

  return (
    <div className="relative flex h-full mx-[20px] flex-col mt-[69px] gap-y-[11px]">
      <div className="text-[16px]">3/4</div>
      <div className="text-[24px]">이렇게 설정할까요?</div>

      <div className="flex flex-col items-start mx-[40px] mt-[90px]">
        {shopTimes.map((t, idx) => (
          <div key={t.label} className="flex items-start gap-3">
            {/* circle + line */}
            <div className="flex flex-col items-center">
              <div className="w-[34px] h-[34px] rounded-full bg-[#D9D9D9]"></div>
              {idx < shopTimes.length - 1 && (
                <div className="w-px h-6 bg-[#D9D9D9]"></div>
              )}
            </div>

            {/* time label */}
            <div className="flex flex-row">
              <span className="text-[18px] mt-1">
                {t.value} {t.label}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ConfirmOp;
