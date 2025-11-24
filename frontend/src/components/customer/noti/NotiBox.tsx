import type { AlarmBaseType } from "@interface/customer/order";
import { formatDate, getStatusLabel } from "@utils";
import { useNavigate } from "react-router-dom";

interface NotiBoxType {
  noti: AlarmBaseType[] | [];
}

export const NotiBox = ({ noti }: NotiBoxType) => {
  const navigate = useNavigate();

  return (
    <div className="m-[20px] flex flex-col gap-y-[20px]">
      {noti.map((n, idx) => (
        <div
          key={idx}
          className="shadow px-[23px] py-[20px] rounded flex flex-col gap-y-[20px] bg-white"
          onClick={() => {
            const nextPath =
              n.status === "cancel" ? "/c/order/all" : "/c/order";
            navigate(nextPath);
          }}
        >
          {/* first row */}
          <div className="font-bold flex flex-row justify-between">
            <div className="tagFont">
              {formatDate(n.order_time)?.slice(0, 16).replaceAll("-", ".")}
            </div>
            <div className="bodyFont">{n.store_name}</div>
          </div>

          {/* second row */}
          <div className="font-bold flex flex-row justify-between">
            <h3
              className={`${
                n.status == "cancel"
                  ? "text-sub-red"
                  : n.status == "accept"
                  ? "text-main-deep"
                  : ""
              }`}
            >
              {getStatusLabel(n.status)}
            </h3>
            <div className="tagFont">{n.product_name}</div>
          </div>

          {/* thrid row */}
          <div className="font-bold flex flex-row justify-between">
            <div className="tagFont">
              픽업: {n.pickup_start_time} ~ {n.pickup_end_time}
            </div>
            <div className="tagFont">
              {Number(n.total_amount).toLocaleString()}원
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};
