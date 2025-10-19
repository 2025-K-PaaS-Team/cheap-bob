type ProgressBarProps = {
  pageIdx: number;
};

const ProgressBar = ({ pageIdx }: ProgressBarProps) => {
  const items = ["매장 등록하기", "운영 정보", "패키지"];

  const handleStep = (pageIdx: number): number => {
    if (pageIdx < 7) {
      return 0;
    } else if (pageIdx < 11) {
      return 1;
    } else {
      return 2;
    }
  };

  const currentStep = handleStep(pageIdx);

  return (
    <div className="grid grid-cols-3 text-center">
      {items.map((item, idx) => (
        <div key={idx} className="flex flex-col items-center">
          <div className="h-[56px] flex items-center">{item}</div>
          {idx === currentStep ? (
            <hr className="w-full border-0 h-[3px] bg-main-deep" />
          ) : (
            <hr />
          )}
        </div>
      ))}
    </div>
  );
};

export default ProgressBar;
