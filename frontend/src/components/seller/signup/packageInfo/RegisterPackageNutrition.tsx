import { CommonBtn, CommonModal, SelectedGrid } from "@components/common";
import { NutritionList } from "@constant";
import type { NutritionBase, SellerSignupPkgProps } from "@interface";
import { validateSelect, validationRules } from "@utils";
import { useState } from "react";

const RegisterPackageNutrition = ({
  pageIdx,
  setPageIdx,
  pkg,
  setPkg,
}: SellerSignupPkgProps) => {
  const [showModal, setShowModal] = useState<boolean>(false);
  const [modalMsg, setModalMsg] = useState("");

  const handleClickNext = () => {
    const { packageSelect } = validationRules;
    if (
      !validateSelect(
        pkg.nutrition_types.length,
        packageSelect.minSelect,
        packageSelect.maxSelect
      )
    ) {
      setModalMsg(packageSelect.errorMessage);
      setShowModal(true);
      return;
    }
    setPageIdx(pageIdx + 1);
  };

  const handleClickPrev = () => {
    setPageIdx(pageIdx - 1);
  };

  const handleClick = (key: NutritionBase) => {
    if (pkg.nutrition_types.includes(key)) {
      setPkg({
        ...pkg,
        nutrition_types: pkg.nutrition_types.filter((item) => item !== key),
      });
    } else {
      setPkg({ ...pkg, nutrition_types: [...pkg.nutrition_types, key] });
    }
  };

  return (
    <div className="flex h-full mx-[20px] flex-col mt-[20px] gap-y-[11px]">
      <div className="text-[16px]">2/4</div>
      <div className="titleFont">
        패키지의 <span className="font-bold">특징</span>은 무엇인가요?
      </div>
      <div className="text-[14px] mb-[36px]">
        최대 3개까지 선택할 수 있어요.
      </div>

      {/* nutrition list */}
      <SelectedGrid
        data={NutritionList}
        selected={pkg.nutrition_types}
        selectType="nutrition"
        onClick={handleClick}
      />

      <CommonBtn
        category="grey"
        label="이전"
        onClick={() => handleClickPrev()}
        notBottom
        className="absolute left-[20px] bottom-[38px]"
        width="w-[100px]"
      />
      <CommonBtn
        category="green"
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
          category="green"
        />
      )}
    </div>
  );
};

export default RegisterPackageNutrition;
