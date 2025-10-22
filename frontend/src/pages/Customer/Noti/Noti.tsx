import { CommonBtn, CommonModal } from "@components/common";
import CommonLoading from "@components/common/CommonLoading";
import type { AlarmBaseType } from "@interface/customer/order";
import { getAlarmToday } from "@services";
import { formatDate, formatErrMsg } from "@utils";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

const Noti = () => {
  const [noti, setNoti] = useState<AlarmBaseType[]>([]);
  const navigate = useNavigate();

  const [showModal, setShowModal] = useState<boolean>(false);
  const [modalMsg, setModalMsg] = useState("");

  const [isLoading, setIsLoading] = useState<boolean>(true);

  const handleGetAlarm = async () => {
    try {
      const res = await getAlarmToday();
      setNoti(res.alarm_cards || []);
    } catch (err) {
      setModalMsg(formatErrMsg(err));
      setShowModal(true);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    handleGetAlarm();
  }, []);

  if (isLoading) {
    return <CommonLoading type="data" isLoading={isLoading} />;
  }

  if (!noti.length) {
    return (
      <div className="flex flex-col h-full justify-center items-center bg-custom-white">
        <img
          src="/icon/angrySalad.svg"
          alt="saladBowlIcon"
          className="pb-[26px] w-[116px]"
        />
        <div className="text-[20px] pb-[17px] font-bold">
          관심 가게가 비어있어요.
        </div>
        <div className="text-[12px] font-base pb-[46px]">
          다양한 랜덤팩을 주문하고 픽업해보세요.
        </div>
        <CommonBtn
          label="실시간 랜덤팩 보러가기"
          notBottom
          width="w-[calc(100%-40px)]"
          onClick={() => navigate("/c/stores")}
        />
      </div>
    );
  }

  const getStatusLabel = (status: string) => {
    if (status == "reservation") {
      return "주문이 들어갔어요!";
    }
    if (status == "accept") {
      return "픽업이 확정됐어요!";
    }
    if (status == "cancel") {
      return "주문이 취소됐어요.";
    } else {
      return "-";
    }
  };

  return (
    <div className="flex flex-col bg-custom-white">
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

        {/* show modal */}
        {showModal && (
          <CommonModal
            desc={modalMsg}
            confirmLabel="확인"
            onConfirmClick={() => setShowModal(false)}
            category="green"
          />
        )}
      </div>
    </div>
  );
};

export default Noti;
