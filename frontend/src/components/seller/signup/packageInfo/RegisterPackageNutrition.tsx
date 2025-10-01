import { SelectedGrid } from "@components/common";
import { NutritionList } from "@constant";
import { useState } from "react";

const RegisterPackageNutrition = () => {
  const [nutrition, setNutrition] = useState<string[]>([]);
  const handleClick = (key: string) => {
    if (nutrition.includes(key)) {
      setNutrition(nutrition.filter((item) => item != key));
    } else {
      setNutrition([...nutrition, key]);
    }
  };

  return (
    <div className="relative flex h-full mx-[20px] flex-col mt-[69px] gap-y-[11px]">
      <div className="text-[16px]">2/4</div>
      <div className="text-[24px]">
        패키지의 <span className="font-bold">특징</span>은 무엇인가요?
      </div>
      <div className="text-[14px] mb-[36px]">
        최대 3개까지 선택할 수 있어요.
      </div>

      {/* nutrition list */}
      <SelectedGrid
        data={NutritionList}
        selected={nutrition}
        selectType="nutrition"
        onClick={handleClick}
      />
    </div>
  );
};

export default RegisterPackageNutrition;
