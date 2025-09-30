import { CommonBtn } from "@components/common";
import { useState } from "react";

type AgreeProps = {
  onNext: () => void;
};

const Agree = ({ onNext }: AgreeProps) => {
  const [agree, setAgree] = useState({
    service: false,
    privacy: false,
  });

  const allAgree = agree.service && agree.privacy;

  const handleChange = (key: "privacy" | "service", value: boolean) => {
    setAgree((prev) => ({ ...prev, [key]: value }));
  };

  const handleAllChange = (checked: boolean) => {
    setAgree({ service: checked, privacy: checked });
  };

  const handleSubmit = () => {
    if (!allAgree) {
      alert("필수 항목에 모두 동의해주세요");
      return;
    }
    console.log("onNext");
    onNext();
  };

  return (
    <div>
      <div className="absolute bottom-[145px] flex flex-col gap-y-[28px]">
        {/* 서비스 동의 */}
        <div className="flex flex-row gap-x-[10px]">
          <input
            type="checkbox"
            checked={agree.service}
            onChange={(e) => handleChange("service", e.target.checked)}
          />
          <div className="font-base">(필수) 서비스 이용약관 동의</div>
          <div className="underline text-[#6C6C6C] fixed right-[20px]">
            보기
          </div>
        </div>
        {/* 개인정보 동의 */}
        <div className="flex flex-row gap-x-[10px]">
          <input
            type="checkbox"
            checked={agree.privacy}
            onChange={(e) => handleChange("privacy", e.target.checked)}
          />
          <div className="font-base">(필수) 개인정보 수집 이용 동의</div>
          <div className="underline text-[#6C6C6C] fixed right-[20px]">
            보기
          </div>
        </div>
        {/* 모두 동의 */}
        <div className="flex flex-row gap-x-[10px] mt-[53px]">
          <input
            type="checkbox"
            checked={allAgree}
            onChange={(e) => handleAllChange(e.target.checked)}
          />
          <div className="font-bold">모두 동의합니다.</div>
        </div>
      </div>
      {/* 다음 */}
      <CommonBtn label="다음" onClick={handleSubmit} notBottom={false} />
    </div>
  );
};

export default Agree;
