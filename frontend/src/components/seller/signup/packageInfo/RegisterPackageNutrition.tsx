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
  const { packageSelect } = validationRules;

  const handleClickNext = () => {
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
    <div className="flex flex-col mx-[20px] flex-col mt-[20px] gap-y-[40px]">
      <div className="text-main-deep font-bold bodyFont">3/5</div>
      <div className="flex flex-col gap-y-[20px]">
        <div className="titleFont">
          <span className="font-bold">패키지의 영양 특징</span>은 무엇인가요?
        </div>
        <div className="hintFont">최대 3개까지 선택할 수 있어요.</div>
      </div>

      {/* nutrition list */}
      <SelectedGrid
        data={NutritionList}
        selected={pkg.nutrition_types}
        selectType="nutrition"
        onClick={handleClick}
      />

      <CommonBtn
        category="transparent"
        label="이전"
        onClick={() => handleClickPrev()}
        notBottom
        className="absolute left-[20px] bottom-[38px]"
        width="w-[100px]"
      />
      <CommonBtn
        category={
          validateSelect(
            pkg.nutrition_types.length,
            packageSelect.minSelect,
            packageSelect.maxSelect
          )
            ? "green"
            : "grey"
        }
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
