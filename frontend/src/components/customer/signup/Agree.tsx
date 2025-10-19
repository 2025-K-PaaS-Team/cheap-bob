import { CommonBtn, CommonModal } from "@components/common";
import { useState } from "react";

type AgreeProps = {
  onNext?: () => void;
};

const Agree = ({ onNext }: AgreeProps) => {
  const [showModal, setShowModal] = useState(false);
  const [modalMsg, setModalMsg] = useState<string>("");

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
    if (!onNext) return;
    if (!allAgree) {
      setModalMsg("필수 항목에 모두 동의해주세요");
      setShowModal(true);
      return;
    }
    onNext();
  };

  return (
    <>
      <div className="absolute bottom-[130px] left-1/2 -translate-x-1/2 flex flex-col w-[calc(100%-40px)] gap-y-[28px]">
        {/* 서비스 동의 */}
        <div className="flex flex-row gap-x-[10px]">
          <input
            type="checkbox"
            checked={agree.service}
            onChange={(e) => handleChange("service", e.target.checked)}
          />
          <div className="bodyFont">(필수) 서비스 이용약관 동의</div>
          <div className="underline text-[#6C6C6C] absolute right-[20px]">
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
          <div className="bodyFont">(필수) 개인정보 수집 이용 동의</div>
          <div className="underline text-[#6C6C6C] absolute right-[20px]">
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
          <h3>모두 동의합니다.</h3>
        </div>
      </div>

      {/* next */}
      {onNext && (
        <CommonBtn
          label="다음"
          onClick={handleSubmit}
          category={allAgree ? "green" : "grey"}
        />
      )}

      {showModal && (
        <CommonModal
          desc={modalMsg}
          confirmLabel="확인"
          onConfirmClick={() => setShowModal(false)}
          category="green"
        />
      )}
    </>
  );
};

export default Agree;
