import type { OperationTimeType } from "@interface";
import { useEffect, useState } from "react";

interface PuTimeProps {
  form: OperationTimeType[];
  setForm: (times: OperationTimeType[]) => void;
}

const CommonPuTime = ({ form, setForm }: PuTimeProps) => {
  const [offsetHour, setOffsetHour] = useState(2);
  const [offsetMin, setOffsetMin] = useState(30);

  useEffect(() => {
    const newForm = form.map((f) => {
      if (!f.close_time) return f;

      const [hh, mm] = f.close_time.split(":").map(Number);
      const closeDate = new Date(2000, 0, 1, hh, mm);

      const pickupDate = new Date(closeDate.getTime());
      pickupDate.setHours(pickupDate.getHours() - offsetHour);
      pickupDate.setMinutes(pickupDate.getMinutes() - offsetMin);

      const phh = String(pickupDate.getHours()).padStart(2, "0");
      const pmm = String(pickupDate.getMinutes()).padStart(2, "0");

      return {
        ...f,
        pickup_start_time: `${phh}:${pmm}:00`,
      };
    });

    setForm(newForm);
  }, [offsetHour, offsetMin]);

  // 월요일(0) pickup 시간 표시용
  const monday = form.find((f) => f.day_of_week === 0);
  const displayPickup = monday?.pickup_start_time || "00:00:00";
  const [dhh, dmm] = displayPickup.split(":");

  return (
    <>
      {/* pickup time */}
      <div className="text-[14px] font-bold">픽업 시간</div>
      <div className="text-[14px]">
        마감 세일을 시작할 시간을 입력해 주세요.
      </div>
      <div className="text-center w-full justify-center">
        {/* before time */}
        <div className="flex flex-row text-[20px] justify-center items-center gap-x-[10px]">
          <input
            className="bg-[#d9d9d9] rounded-[8px] w-[50px] h-[44px] text-center"
            value={offsetHour}
            onChange={(e) => setOffsetHour(Number(e.target.value))}
          />
          <div>시</div>
          <input
            className="bg-[#d9d9d9] rounded-[8px] w-[50px] h-[44px] text-center"
            value={offsetMin}
            onChange={(e) => setOffsetMin(Number(e.target.value))}
          />
          <div>분 전부터</div>
        </div>
        <div className="text-[14px] mt-[10px]">
          월요일 기준 {dhh}시 {dmm}분부터 사용자들은 매장에 방문하여 <br />{" "}
          패키지를 픽업할 수 있습니다.
        </div>
      </div>

      {/* after time */}
      <div className="text-[14px] font-bold mt-[40px]">픽업 마감 시간</div>
      <div className="text-[14px]">픽업을 마감할 시간을 입력해 주세요.</div>
      <div className="text-center w-full justify-center">
        {/* close_time 직접 입력받을 수도 있음 */}
        <div className="flex flex-row text-[20px] justify-center items-center gap-x-[10px]">
          <div className="bg-[#d9d9d9] rounded-[8px] w-[50px] h-[44px] flex items-center justify-center">
            {monday?.close_time.split(":")[0] || "--"}
          </div>
          <div>시</div>
          <div className="bg-[#d9d9d9] rounded-[8px] w-[50px] h-[44px] flex items-center justify-center">
            {monday?.close_time.split(":")[1] || "--"}
          </div>
          <div>분까지</div>
        </div>
        <div className="text-[14px] mt-[10px]">
          월요일 기준 {monday?.close_time || "00:00:00"}까지 픽업이 가능합니다.
        </div>
      </div>
    </>
  );
};

export default CommonPuTime;
