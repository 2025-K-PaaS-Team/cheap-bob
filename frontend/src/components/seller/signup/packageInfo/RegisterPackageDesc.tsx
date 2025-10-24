import { CommonBtn, CommonModal } from "@components/common";
import type { SellerSignupPkgProps } from "@interface";
import { validateLength, validationRules } from "@utils";
import { useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

const RegisterPackageDesc = ({ pkg, setPkg }: SellerSignupPkgProps) => {
  const navigate = useNavigate();
  const { pageIdx: paramPageIdx } = useParams<{ pageIdx?: string }>();
  const pageIdx = Number(paramPageIdx) ?? 0;
  const [showModal, setShowModal] = useState<boolean>(false);
  const [modalMsg, setModalMsg] = useState("");
  const { packageDesc } = validationRules;

  const handleClickNext = () => {
    if (
      !validateLength(
        pkg?.description,
        packageDesc.minLength,
        packageDesc.maxLength
      )
    ) {
      setModalMsg(packageDesc.errorMessage);
      setShowModal(true);
      return;
    }
    navigate(`/s/signup/${pageIdx + 1}`);
  };

  const handleClickPrev = () => {
    navigate(`/s/signup/${pageIdx - 1}`);
  };

  return (
    <div className="mx-[20px] my-[20px] flex flex-col flex-1 gap-y-[40px]">
      <div className="flex flex-1 flex-col gap-y-[40px]">
        <div className="flex flex-1 flex-col gap-y-[20px]">
          <div className="text-main-deep font-bold bodyFont">2/5</div>
          <div className="titleFont">
            <span className="font-bold">패키지 소개</span>를<br /> 입력해
            주세요.
          </div>
          {/* input box */}
          <textarea
            className="w-full h-[145px] rounded border border-[#E7E7E7] text-[16px] mt-[40px] p-[8px]"
            placeholder="텍스트를 입력하세요"
            value={pkg?.description}
            onChange={(e) =>
              setPkg((prev) => ({ ...prev, description: e.target.value }))
            }
          />
        </div>
      </div>

      <div className="grid grid-cols-3 my-[20px]">
        <CommonBtn
          category="transparent"
          label="이전"
          onClick={() => handleClickPrev()}
          notBottom
        />
        <CommonBtn
          category={
            validateLength(
              pkg?.description,
              packageDesc.minLength,
              packageDesc.maxLength
            )
              ? "green"
              : "grey"
          }
          label="다음"
          onClick={() => handleClickNext()}
          className="col-span-2"
          notBottom
        />
      </div>

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

export default RegisterPackageDesc;
