import { NutritionList } from "@constant";
import type { PreferNutritionBaseType } from "@interface";
import { getTitleByKey } from "@utils";
import { useNavigate } from "react-router-dom";

interface NutritionGoalType {
  nutrition: PreferNutritionBaseType[] | null;
}

export const NutritionGoal = ({ nutrition }: NutritionGoalType) => {
  const navigate = useNavigate();

  return (
    <div
      onClick={() => navigate("/c/change/nutrition")}
      className="bg-main-pale border border-main-deep rounded w-full py-[20px] px-[15px]"
    >
      <h1 className="pb-[21px]">영양 목표</h1>
      <div className="flex flex-row gap-x-[5px]">
        {nutrition?.map((n, idx) => (
          <div
            key={idx}
            className="tagFont font-bold bg-black rounded text-white px-[10px] py-[7px]"
          >
            {getTitleByKey(n.nutrition_type, NutritionList)}
          </div>
        ))}
      </div>
    </div>
  );
};
