import { CommonBtn } from "@components/common";
import { daysOfWeek } from "@constant";
import { useState } from "react";
import { useNavigate } from "react-router";

const ChangeOperationTime = () => {
  const [opDay, setOpDay] = useState<number[]>([]);
  const navigate = useNavigate();

  const handleClickDays = (idx: number) => {
    setOpDay((prev) =>
      prev.includes(idx) ? prev.filter((day) => day !== idx) : [...prev, idx]
    );
  };

  const handleSubmit = () => {
    navigate(-1);
  };

  return (
    <div className="relative flex h-full mx-[20px] flex-col">
      {/* operation days */}
      <div className="flex flex-col gap-y-[10px]">
        <div className="text-[14px] font-bold">운영 요일</div>
        <div className="text-[14px]">
          매장을 운영하는 날짜를 모두 선택해 주세요.
        </div>
        <div className="grid grid-cols-7">
          {daysOfWeek.map((day) => (
            <div
              className={`text-[20px] h-[40px] w-[40px] aspect-square text-center flex justify-center items-center rounded-full ${
                opDay.includes(day.idx) ? "bg-[#d9d9d9]" : ""
              }`}
              key={day.idx}
              onClick={() => handleClickDays(day.idx)}
            >
              {day.label}
            </div>
          ))}
        </div>
      </div>

      {/* operation time */}
      <div className="flex flex-col mt-[40px] gap-y-[10px]">
        <div className="text-[14px] font-bold">매장 운영 시간</div>
        <div className="text-[14px]">매장을 운영하는 시간을 입력해 주세요.</div>
        {/* batch time ck box */}
        <div className="flex flex-row gap-x-[22px]h">
          <input type="checkbox" id="batchTime" />
          <span>시간 일괄 적용</span>
        </div>
        {/* list header*/}
        <div className="grid grid-cols-8">
          <div />
          <div className="col-span-3 text-center">매장 오픈</div>
          <div />
          <div className="col-span-3 text-center">매장 마감</div>
        </div>

        {/* list content */}
        <div className="flex flex-col items-center">
          {daysOfWeek.map((day) => (
            <div className="grid grid-cols-8 w-full items-center" key={day.idx}>
              {/* 1 col */}
              <div className="font-bold text-[14px] h-[40px] flex items-center justify-center">
                {day.label}
              </div>
              {/* 2~3col */}
              <div className="col-span-3 text-center flex flex-row gap-x-[5px] justify-center">
                <div className="bg-[#d9d9d9] rounded-[8px] w-[36px]">9</div>
                <div className="">시</div>
                <div className="bg-[#d9d9d9] rounded-[8px] w-[36px]">30</div>
                <div className="">분</div>
              </div>
              {/* 4~5col */}
              <div className="text-center font-bold">~</div>
              {/* 6~7col */}
              <div className="col-span-3 text-center flex flex-row gap-x-[5px] justify-center">
                <div className="bg-[#d9d9d9] rounded-[8px] w-[36px]">9</div>
                <div className="">시</div>
                <div className="bg-[#d9d9d9] rounded-[8px] w-[36px]">30</div>
                <div className="">분</div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* notice */}
      <div className="absolute bottom-30 w-[350px] left-1/2 -translate-x-1/2 bg-[#d9d9d9] rounded-[8px] h-[57px] px-[10px] flex items-center">
        변경시 다음 영업일부터 적용됩니다.
      </div>

      {/* btn */}
      <CommonBtn
        label="다음"
        onClick={handleSubmit}
        className="bg-black text-white"
      />
    </div>
  );
};

export default ChangeOperationTime;
