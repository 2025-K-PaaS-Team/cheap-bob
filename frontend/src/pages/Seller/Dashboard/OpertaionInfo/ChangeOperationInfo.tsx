import { useNavigate } from "react-router";

const ChangeOperationInfo = () => {
  const navigate = useNavigate();
  const items = [
    { label: "운영 시간 변경", to: "/s/change/operation/op-time" },
    { label: "픽업 시간 변경", to: "/s/change/operation/pu-time" },
  ];

  return (
    <div className="mx-[35px]">
      {/* now op time */}
      <div className="flex flex-col">
        <div className="text-[16px]">현재 운영 정보</div>
        <div className="bg-[#D9D9D9] rounded-[8px] my-[8px] flex flex-col py-[15px] px-[23px] space-y-[10px]">
          <div className="flex flex-row grid grid-cols-3 items-center">
            <div className="text-[14px]">운영 시간</div>
            <div className="text-[20px] col-span-2 text-center">21:30</div>
          </div>
          <div className="flex flex-row grid grid-cols-3 items-center">
            <div className="text-[14px]">오픈 시간</div>
            <div className="text-[20px] col-span-2 text-center">21:30</div>
          </div>
          <div className="flex flex-row grid grid-cols-3 items-center">
            <div className="text-[14px]">픽업 확정 시간</div>
            <div className="text-[20px] col-span-2 text-center">21:30</div>
          </div>
          <div className="flex flex-row grid grid-cols-3 items-center">
            <div className="text-[14px]">픽업 마감 시간</div>
            <div className="text-[20px] col-span-2 text-center">21:30</div>
          </div>
          <div className="flex flex-row grid grid-cols-3 items-center">
            <div className="text-[14px]">마감 시간</div>
            <div className="text-[20px] col-span-2 text-center">21:30</div>
          </div>
        </div>
      </div>
      {/* change op, pu time */}
      {items.map((item, idx) => (
        <div key={idx}>
          <div
            className="text-[16px] py-[20px] border-b-[1px] border-black/10"
            onClick={() => navigate(item.to)}
          >
            {item.label}
          </div>
        </div>
      ))}
    </div>
  );
};

export default ChangeOperationInfo;
