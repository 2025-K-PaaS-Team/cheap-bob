import { QRCodeSVG } from "qrcode.react";
import CommonBtn from "./CommonBtn";

interface CommonQRPros {
  onClick: () => void;
}

const CommonQR = ({ onClick }: CommonQRPros) => {
  const qrValue = "hello";

  return (
    <div className="fixed inset-0 flex items-center justify-center bg-black/50 z-50">
      <div className="flex flex-col w-[359px] p-[20px] rounded-[16px] gap-y-[10px] border-[1px] border-black bg-white items-center">
        <div className="text-[16px] text-center">
          손님에게 아래 QR코드를 보여주세요.
          <br />
          QR코드를 찍으면 픽업이 완료됩니다.
        </div>
        <QRCodeSVG value={qrValue} size={200} />
        <div className="flex flex-row gap-x-[20px] text-[18px] text-center">
          <CommonBtn
            label="취소"
            category="white"
            onClick={onClick}
            notBottom
            width="w-[300px]"
            className="rounded-[16px]"
          />
        </div>
      </div>
    </div>
  );
};

export default CommonQR;
