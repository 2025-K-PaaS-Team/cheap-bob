import { QRCodeSVG } from "qrcode.react";
import CommonBtn from "./CommonBtn";
import type { GetQrCodeType } from "@interface";

interface CommonQRPros {
  onClick: () => void;
  qrData: GetQrCodeType;
}

const CommonQR = ({ onClick, qrData }: CommonQRPros) => {
  // const qrValue = JSON.stringify({
  //   payment_id: qrData.payment_id,
  //   qr_data: qrData.qr_data,
  // });
  const qrValue = qrData.qr_data;

  return (
    <div className="fixed inset-0 flex items-center justify-center bg-black/50 z-50">
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
    </div>
  );
};

export default CommonQR;
