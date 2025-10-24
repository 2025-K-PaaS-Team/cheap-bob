import { CommonBtn, CommonModal } from "@components/common";
import type { SellerSignupPkgProps } from "@interface";
import { validateLength, validationRules } from "@utils";
import { useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

const RegisterPackageName = ({ pkg, setPkg }: SellerSignupPkgProps) => {
  const { pageIdx: paramPageIdx } = useParams<{ pageIdx?: string }>();
  const pageIdx = Number(paramPageIdx) ?? 0;
  const [showModal, setShowModal] = useState<boolean>(false);
  const [modalMsg, setModalMsg] = useState("");
  const { packageName } = validationRules;
  const navigate = useNavigate();

  const handleClickNext = () => {
    if (
      !validateLength(
        pkg?.product_name,
        packageName.minLength,
        packageName.maxLength
      )
    ) {
      setModalMsg(packageName.errorMessage);
      setShowModal(true);
      return;
    }

    navigate(`/s/signup/${pageIdx + 1}`);
  };

  console.log(pkg);

  return (
    <div className="mx-[20px] my-[20px] flex flex-col flex-1 gap-y-[40px]">
      <div className="flex flex-1 flex-col gap-y-[40px]">
        <div className="flex flex-1 flex-col gap-y-[20px]">
          <div className="text-main-deep font-bold bodyFont">1/5</div>
          <div className="titleFont">
            <span className="font-bold">패키지 이름</span>을<br /> 입력해
            주세요.
          </div>

          {/* input box */}
          <input
            className="w-full h-[46px] border-b  border-[#393939] hintFont mt-[40px]"
            placeholder="텍스트를 입력하세요"
            value={pkg?.product_name}
            onChange={(e) =>
              setPkg((prev) => ({ ...prev, product_name: e.target.value }))
            }
          />
        </div>
      </div>

      <CommonBtn
        label="다음"
        onClick={() => handleClickNext()}
        notBottom
        className="my-[20px]"
        category={
          validateLength(
            pkg?.product_name,
            packageName.minLength,
            packageName.maxLength
          )
            ? "green"
            : "grey"
        }
      />

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

export default RegisterPackageName;
