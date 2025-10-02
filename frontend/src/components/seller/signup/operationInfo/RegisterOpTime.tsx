import { CommonBtn, CommonModal } from "@components/common";
import type { SellerSignupProps } from "@interface";
import { useSignupStore } from "@store";
import { validateLength, validationRules } from "@utils";
import { useState } from "react";

const RegisterOpTime = ({ pageIdx, setPageIdx }: SellerSignupProps) => {
  const { form, setForm } = useSignupStore();
  const [showModal, setShowModal] = useState<boolean>(false);
  const [modalMsg, setModalMsg] = useState("");

  const handleClickNext = () => {
    const { storeName } = validationRules;
    if (
      !validateLength(form.store_name, storeName.minLength, storeName.maxLength)
    ) {
      setModalMsg(storeName.errorMessage);
      setShowModal(true);
      return;
    }
    setPageIdx(pageIdx + 1);
  };

  const [opDay, setOpDay] = useState<number[]>([]);
  const daysOfWeek = [
    { label: "월", idx: 0 },
    { label: "화", idx: 1 },
    { label: "수", idx: 2 },
    { label: "목", idx: 3 },
    { label: "금", idx: 4 },
    { label: "토", idx: 5 },
    { label: "일", idx: 6 },
  ];

  const handleClickDays = (idx: number) => {
    setOpDay((prev) =>
      prev.includes(idx) ? prev.filter((day) => day !== idx) : [...prev, idx]
    );
  };

  return (
    <div className="flex mx-[20px] flex-col mt-[69px] gap-y-[11px]">
      <div className="text-[16px]">1/4</div>
      <div className="text-[24px]">
        매장의
        <span className="font-bold">오픈 시간</span>과 <br />{" "}
        <span className="font-bold">매감 시간</span>을 알려주세요.
      </div>

      {/* operation days */}
      <div className="flex flex-col gap-y-[10px] mt-[38px]">
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
        <div className="flex flex-row gap-x-[22px]">
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
        <div className="flex flex-col items-center overflow-y-auto h-[220px]">
          {daysOfWeek
            .filter((day) => opDay.includes(day.idx))
            .sort((a, b) => a.idx - b.idx)
            .map((day) => (
              <div
                className="grid grid-cols-8 w-full items-center"
                key={day.idx}
              >
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

      <CommonBtn
        category="black"
        label="다음"
        onClick={() => handleClickNext()}
      />

      {/* show modal */}
      {showModal && (
        <CommonModal
          desc={modalMsg}
          confirmLabel="확인"
          onConfirmClcik={() => setShowModal(false)}
          category="black"
        />
      )}
    </div>
  );
};

export default RegisterOpTime;
