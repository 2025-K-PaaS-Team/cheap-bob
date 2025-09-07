import { QRCodeSVG } from "qrcode.react";
import { useState } from "react";
import { QrReader } from "react-qr-reader";

const QrLab = () => {
  const [qrValue, setQrValue] = useState<string>("");
  const [data, setData] = useState<string>();

  return (
    <div className="flex flex-col w-full items-center gap-y-3 justify-center align-center">
      <div>QR LAB</div>
      {/* qr creator */}
      <QRCodeSVG value={qrValue} size={100} />
      <input
        type="text"
        className="w-80 border-1"
        value={qrValue}
        onChange={(e) => setQrValue(e.target.value)}
        placeholder="생성하고 싶은 qr코드 정보를 입력해주세요"
      />

      {/* qr reader */}
      <div style={{ width: "300px", margin: "auto" }}>
        <QrReader
          constraints={{ facingMode: "environment" }}
          onResult={(result, error) => {
            if (result) setData(result.getText());
            if (error) console.log(error);
          }}
        />
        <div>qr을 스캔하면 아래 칸에 데이터가 나옵니다</div>
        <div className="border border-1">데이터: {data}</div>
      </div>
    </div>
  );
};

export default QrLab;
