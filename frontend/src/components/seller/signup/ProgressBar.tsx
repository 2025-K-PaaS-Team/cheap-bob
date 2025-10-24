import { useParams } from "react-router-dom";

const ProgressBar = () => {
  const items = ["매장 등록", "운영 정보 등록", "패키지 등록"];
  const { pageIdx } = useParams<{ pageIdx?: string }>();

  const handleStep = (pageIdx: number): number => {
    if (pageIdx < 7) {
      return 0;
    } else if (pageIdx < 10) {
      return 1;
    } else {
      return 2;
    }
  };

  const currentStep = handleStep(Number(pageIdx));

  return (
    <div className="grid grid-cols-3 text-center">
      {items.map((item, idx) => (
        <div key={idx} className="flex flex-col items-center">
          <div
            className={` ${
              idx === currentStep ? "font-bold" : ""
            } h-[56px] flex items-center`}
          >
            {item}
          </div>
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
