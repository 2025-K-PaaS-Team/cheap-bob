import { CommonBtn, CommonModal } from "@components/common";
import type { SellerSignupPkgProps } from "@interface";
import { validateNum, validationRules } from "@utils";
import { useState } from "react";

const RegisterPackageNum = ({
  pageIdx,
  setPageIdx,
  pkg,
  setPkg,
}: SellerSignupPkgProps) => {
  const [showModal, setShowModal] = useState<boolean>(false);
  const [modalMsg, setModalMsg] = useState("");

  const handleClickNext = () => {
    const { packageStock } = validationRules;
    if (!validateNum(pkg.initial_stock, packageStock.minStock)) {
      setModalMsg(packageStock.errorMessage);
      setShowModal(true);
      return;
    }
    setPageIdx(pageIdx + 1);
  };

  const handleClickPrev = () => {
    setPageIdx(pageIdx - 1);
  };
  return (
    <div className="flex min-h-screen mx-[20px] flex-col mt-[69px] gap-y-[11px]">
      <div className="text-[16px]">4/4</div>
      {/* question */}
      <div className="text-[24px]">하루에 몇 개 판매할까요?</div>
      <div className="text-[14px] font-bold mt-[31px]">패키지 판매 기본값</div>
      <div className="text-[14px] mt-[10px]">
        하루에 판매할 것으로 예상되는 재고 개수를 입력해 주세요. 평균적으로 n개
        판매해요.
      </div>
      <div className="flex flex-row items-center justify-center gap-x-[10px] mt-[10px]">
        <div className="text-[24px]">{pkg.initial_stock}</div>
        <div className="flex flex-col text-[10px]">
          <div
            onClick={() =>
              setPkg((prev) => ({
                ...prev,
                initial_stock: Number(prev.initial_stock + 1),
              }))
            }
          >
            ▲
          </div>
          <div
            onClick={() =>
              setPkg((prev) => ({
                ...prev,
                initial_stock: Number(prev.initial_stock - 1),
              }))
            }
          >
            ▼
          </div>
        </div>
        <div className="text-[20px]">개 판매할게요.</div>
      </div>

      {/* notice */}
      <div className="text-[14px] absolute bottom-100 w-[350px] left-1/2 -translate-x-1/2 bg-[#d9d9d9] rounded-[8px] h-[88px] px-[10px] flex flex-col flex justify-center">
        <div className="font-bold">Tip</div>
        <div>
          설정한 기본값보다 판매할 재고가 남거나 부족해도 <br /> ‘일일
          조정값’으로 매일 조정할 수 있어요.
        </div>
      </div>

      <CommonBtn
        category="grey"
        label="이전"
        onClick={() => handleClickPrev()}
        notBottom
        className="absolute left-[20px] bottom-[38px]"
        width="w-[100px]"
      />
      <CommonBtn
        category="black"
        label="다음"
        onClick={() => handleClickNext()}
        notBottom
        className="absolute right-[20px] bottom-[38px]"
        width="w-[250px]"
      />

      {/* show modal */}
      {showModal && (
        <CommonModal
          desc={modalMsg}
          confirmLabel="확인"
          onConfirmClick={() => setShowModal(false)}
          category="black"
        />
      )}
    </div>
  );
};

export default RegisterPackageNum;
