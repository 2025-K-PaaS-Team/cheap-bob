import { CommonBtn } from "@components/common";
import type { SellerSignupProps } from "@interface";
import { useSignupStore } from "@store";

const ConfirmOp = ({ pageIdx, setPageIdx }: SellerSignupProps) => {
  const { form } = useSignupStore();
  const shopTimes = [
    {
      label: "오픈",
      value: form.operation_times[0].open_time.slice(0, 5),
    },
    {
      label: "픽업 시작",
      value: form.operation_times[0].pickup_start_time.slice(0, 5),
    },
    {
      label: "픽업 마감",
      value: form.operation_times[0].pickup_end_time.slice(0, 5),
    },
    {
      label: "마감",
      value: form.operation_times[0].close_time.slice(0, 5),
    },
  ];

  const handleClickNext = () => {
    setPageIdx(pageIdx + 1);
  };

  const handleClickPrev = () => {
    setPageIdx(pageIdx - 1);
  };

  return (
    <div className="flex mx-[37px] flex-col mt-[125px] gap-y-[11px]">
      <div className="text-[16px]">3/4</div>
      <div className="text-[24px]">이렇게 설정할까요?</div>

      <div className="flex flex-col items-start mx-[23px] mt-[90px]">
        {shopTimes.map((t, idx) => (
          <div key={t.label} className="flex items-start gap-3">
            {/* circle + line */}
            <div className="flex flex-col items-center">
              <div className="w-[34px] h-[34px] rounded-full bg-[#D9D9D9]"></div>
              {idx < shopTimes.length - 1 && (
                <div className="w-px h-[27px] bg-[#D9D9D9]"></div>
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

        <CommonBtn
          category="grey"
          label="이전"
          onClick={() => handleClickPrev()}
          notBottom
          className="absolute left-[20px] bottom-[38px]"
          width="w-[100px]"
        />
        <CommonBtn
          category="black"
          label="설정 완료"
          onClick={() => handleClickNext()}
          notBottom
          className="absolute right-[20px] bottom-[38px]"
          width="w-[250px]"
        />
      </div>
    </div>
  );
};

export default ConfirmOp;
