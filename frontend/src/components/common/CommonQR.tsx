import { QRCodeSVG } from "qrcode.react";
import CommonBtn from "./CommonBtn";
import type { GetQrCodeType } from "@interface";
import { connectOrderSocket } from "@services";
import { useEffect, useState } from "react";
import CommonModal from "./CommonModal";

interface CommonQRPros {
  onClick: () => void;
  onRefresh: () => void;
  qrData: GetQrCodeType;
}

const CommonQR = ({ onClick, onRefresh, qrData }: CommonQRPros) => {
  const [modalMsg, setModalMsg] = useState("");
  const [showModal, setShowModal] = useState<boolean>(false);

  const qrValue = qrData.qr_data;

  useEffect(() => {
    const { ws } = connectOrderSocket(qrData.payment_id, (status) => {
      if (status === "completed") {
        setModalMsg("픽업이 성공적으로 완료되었습니다!");
        setShowModal(true);
      } else if (status === "error") {
        setModalMsg("오류가 발생했습니다. 다시 시도해주세요.");
        setShowModal(true);
      } else if (status === "timeout") {
        setModalMsg("QR 시간이 만료되었습니다. 다시 시도해주세요.");
        setShowModal(true);
      }
    });

    return () => {
      ws.close();
    };
  }, [onClick]);

  return (
    <div className="absolute inset-0 z-[1000] flex items-center justify-center bg-black/20">
      <div className="flex flex-col w-[353px] h-[379px] p-[20px] rounded gap-y-[20px] border-[1px] border-none bg-white items-center justify-center">
        <div className="bodyFont text-center">
          손님에게 아래 QR코드를 보여주세요.
          <br />
          QR코드를 찍으면 픽업이 완료됩니다.
        </div>
        <QRCodeSVG value={qrValue} size={175} />
        <div className="flex flex-row gap-x-[20px] btnFont text-center">
          <CommonBtn
            label="취소"
            category="white"
            onClick={onClick}
            notBottom
            width="w-[300px]"
            className="border-none text-sub-red"
          />
        </div>
      </div>

      {/* show modal */}
      {showModal && (
        <CommonModal
          desc={modalMsg}
          confirmLabel="확인"
          onConfirmClick={() => {
            setShowModal(false);
            onClick();
            onRefresh();
          }}
          category="green"
        />
      )}
    </div>
  );
};

export default CommonQR;
