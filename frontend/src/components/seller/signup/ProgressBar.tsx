type ProgressBarProps = {
  pageIdx: number;
};

const ProgressBar = ({ pageIdx }: ProgressBarProps) => {
  const items = ["매장 등록하기", "운영 정보", "패키지"];
  const step = Math.floor((pageIdx - 1) / 3);

  return (
    <div className="grid grid-cols-3 text-center">
      {items.map((item, idx) => (
        <div key={idx} className="flex flex-col items-center">
          <div className="h-[56px] flex items-center">{item}</div>
          {idx === step ? (
            <hr className="w-full border-0 h-[3px] bg-black" />
          ) : (
            <hr className="w-full border-0 h-[3px] bg-black/20" />
          )}
        </div>
      ))}
    </div>
  );
};

export default ProgressBar;
