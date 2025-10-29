import { useEffect, useState } from "react";

const Inspection = () => {
  const [show, setShow] = useState(false);

  useEffect(() => {
    const checkMaintenance = () => {
      const now = new Date();
      const seoulStr = now.toLocaleString("en-US", { timeZone: "Asia/Seoul" });
      const seoulNow = new Date(seoulStr);
      const hour = seoulNow.getHours();

      setShow(hour >= 18 && hour < 20);
    };

    checkMaintenance();
    const timer = setInterval(checkMaintenance, 60 * 1000);
    return () => clearInterval(timer);
  }, []);

  if (!show) return null;

  return (
    <div className="flex flex-col flex-1 items-center justify-center text-center mx-auto w-full gap-y-[28px] bg-white">
      <img
        src="/icon/greySalad.svg"
        alt="saladBowlIcon"
        className="pb-[40px] w-[116px]"
      />
      <div className="flex flex-col gap-y-[16px]">
        <h1>지금은 점검 시간입니다.</h1>
        <div className="hintFont">점검 시간: 오전 4시 ~ 오전 5시</div>
      </div>
    </div>
  );
};

export default Inspection;
