import { GetStoreReservation } from "@services";
import { useDashboardStore } from "@store";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

const ChangePackageInfo = () => {
  const navigate = useNavigate();
  const [reservation, setReservation] = useState<string>();
  const repProductId = useDashboardStore((s) => s.repProductId);

  const items = [
    { label: "패키지 이름 변경", to: "/s/change/package/name" },
    { label: "패키지 소개 변경", to: "/s/change/package/desc" },
    { label: "영양목표 변경", to: "/s/change/package/nutrition" },
    { label: "패키지 가격 변경", to: "/s/change/package/price" },
    { label: "판매 기본값 변경", to: "/s/change/package/num" },
  ];

  useEffect(() => {
    const init = async () => {
      const res = await GetStoreReservation(repProductId ?? "");
      setReservation(res.reserved_at);
    };
    init();
  }, []);

  return (
    <div className="mx-[35px]">
      {items.map((item, idx) => (
        <div key={idx}>
          <div
            className="flex flex-row items-center justify-between text-[16px] py-[20px] border-b-[1px] border-black/10"
            onClick={() => navigate(item.to)}
          >
            {item.label}
            {reservation && item.label === "판매 기본값 변경" && (
              <div className="tagFont w-fit text-nowrap font-bold bg-main-pale border border-main-deep text-main-deep rounded-sm py-[8px] px-[16px]">
                변경 예약중
              </div>
            )}
          </div>
        </div>
      ))}
    </div>
  );
};

export default ChangePackageInfo;
