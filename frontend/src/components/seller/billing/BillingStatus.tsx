import { BillingOption } from "@constant";

interface BillingStatusProps {
  nowStatus: string;
  setNowStatus: (nowStatus: string) => void;
}

const BillingStatus = ({ nowStatus, setNowStatus }: BillingStatusProps) => {
  return (
    <div className="flex flex-row items-center gap-x-[10px] text-nowrap">
      <div className="font-bold mr-auto">상태</div>

      {BillingOption.map((status, idx) => (
        <div
          key={idx}
          onClick={() => setNowStatus(status.key)}
          className={`${
            nowStatus == status.key
              ? "bg-main-pale border border-main-deep text-main-deep"
              : ""
          } w-fit py-[8px] px-[16px] rounded tagFont`}
        >
          {status.title}
        </div>
      ))}
    </div>
  );
};

export default BillingStatus;
