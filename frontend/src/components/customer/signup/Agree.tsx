import { CommonBtn, CommonModal } from "@components/common";
import { useState } from "react";
import { useNavigate } from "react-router";

type AgreeProps = {
  onNext?: () => void;
};

const Agree = ({ onNext }: AgreeProps) => {
  const navigate = useNavigate();
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
      <div className="flex flex-col justify-end mx-auto w-[calc(100%-40px)] gap-y-[28px]">
        {/* 서비스 동의 */}
        <div className="flex flex-row justify-between">
          <div className="flex flex-row gap-x-[10px] flex-1">
            <input
              type="checkbox"
              checked={agree.service}
              onChange={(e) => handleChange("service", e.target.checked)}
            />
            <div className="bodyFont flex-1">(필수) 서비스 이용약관 동의</div>
          </div>
          <div
            className="underline text-[#6C6C6C]"
            onClick={() => navigate("/docs/tos")}
          >
            보기
          </div>
        </div>
        {/* 개인정보 동의 */}
        <div className="flex flex-row justify-between">
          <div className="flex flex-row gap-x-[10px] flex-1">
            <input
              type="checkbox"
              checked={agree.privacy}
              onChange={(e) => handleChange("privacy", e.target.checked)}
            />
            <div className="bodyFont text-nowrap">
              (필수) 개인정보 수집 이용 동의
            </div>
          </div>

          <div
            className="underline text-[#6C6C6C]"
            onClick={() => navigate("/docs/privacy")}
          >
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

        {/* next */}
        {onNext && (
          <CommonBtn
            label="다음"
            notBottom
            onClick={handleSubmit}
            category={allAgree ? "green" : "grey"}
          />
        )}
      </div>

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
