import { CommonBtn } from "@components/common";
import { useNavigate, useParams } from "react-router-dom";

const SuccessSetting = () => {
  const { pageIdx: paramPageIdx } = useParams<{ pageIdx?: string }>();
  const pageIdx = Number(paramPageIdx) ?? 0;
  const navigate = useNavigate();
  const handleClickNext = () => {
    if (pageIdx < 15) {
      navigate(`/s/signup/${pageIdx + 1}`);
    } else {
      navigate("/s/dashboard");
    }
  };

  const label = (pageIdx: number): string => {
    if (pageIdx < 7) {
      return "매장";
    } else if (pageIdx < 10) {
      return "영업";
    } else {
      return "패키지";
    }
  };

  return (
    <div className="mx-[20px] flex flex-col flex-1 h-full">
      <div className="flex flex-1 flex-col gap-y-[40px] items-center justify-center">
        <img src="/icon/happySalad.svg" alt="happySaldIcon" width="116px" />
        <div className="titleFont font-bold">
          {label(pageIdx)} 정보 등록 완료!
        </div>
        {/* ck box */}
        <div className="flex flex-col bodyFont rounded bg-custom-white min-w-[239px] gap-y-[20px] py-[20px] justify-center items-center">
          <div className="flex flex-row gap-x-[10px]">
            <input type="checkbox" checked={pageIdx > 5 ? true : false} />
            <div>매장 정보 등록</div>
          </div>
          <div className="flex flex-row gap-x-[10px]">
            <input type="checkbox" checked={pageIdx > 8 ? true : false} />
            <div>운영 정보 등록</div>
          </div>
          <div className="flex flex-row gap-x-[10px]">
            <input type="checkbox" checked={pageIdx > 14 ? true : false} />
            <div>패키지 등록</div>
          </div>
        </div>
      </div>

      <CommonBtn
        category="green"
        label="다음"
        notBottom
        className="my-[20px]"
        onClick={() => handleClickNext()}
      />
    </div>
  );
};

export default SuccessSetting;
