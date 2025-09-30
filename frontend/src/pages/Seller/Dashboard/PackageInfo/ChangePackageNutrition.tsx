import { CommonBtn, SelectedGrid } from "@components/common";
import { NutritionList } from "@constant";
import { useState } from "react";
import { useNavigate } from "react-router";

const ChangePackageNutrition = () => {
  const navigate = useNavigate();
  const handleSubmit = () => {
    navigate(-1);
  };

  const [nutrition, setNutrition] = useState<string[]>([]);
  const handleClick = (key: string) => {
    if (nutrition.includes(key)) {
      setNutrition(nutrition.filter((item) => item != key));
    } else {
      setNutrition([...nutrition, key]);
    }
  };

  return (
    <div className="mt-[80px] px-[20px] w-full">
      {/* question */}
      <div className="text-[24px]">패키지의 특징은 무엇인가요?</div>
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
      {/* save */}
      <CommonBtn
        label="저장"
        onClick={handleSubmit}
        className="bg-black text-white"
      />
    </div>
  );
};

export default ChangePackageNutrition;
