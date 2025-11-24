import { CommonModal } from "@components/common";
import CommonLoading from "@components/common/CommonLoading";
import { NoNotiBox, NotiBox } from "@components/customer/noti";
import type { AlarmBaseType } from "@interface/customer/order";
import { getAlarmToday } from "@services";
import { formatErrMsg } from "@utils";
import { useEffect, useState } from "react";

const Noti = () => {
  const [noti, setNoti] = useState<AlarmBaseType[]>([]);

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
    return <NoNotiBox />;
  }

  return (
    <div className="flex flex-col flex-1 bg-custom-white">
      <NotiBox noti={noti} />

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
  );
};

export default Noti;
