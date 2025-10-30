import { CommonBtn, CommonModal, SelectedGrid } from "@components/common";
import CommonLoading from "@components/common/CommonLoading";
import { NutritionList } from "@constant";
import { useToast } from "@context";
import { CrateNutrition, DeleteNutrition, GetNutrition } from "@services";
import { formatErrMsg } from "@utils";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

const ChangeCustomerNutrition = () => {
  const { showToast } = useToast();
  const navigate = useNavigate();
  const [selected, setSelected] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  const [showModal, setShowModal] = useState<boolean>(false);
  const [modalMsg, setModalMsg] = useState("");

  const handleGetNutrition = async () => {
    try {
      const res = await GetNutrition();
      const init = Array.isArray((res as any).nutrition_types)
        ? res.nutrition_types.map((item) => item.nutrition_type)
        : [];
      setSelected(init);
    } catch (err) {
      setModalMsg(formatErrMsg(err));
      setShowModal(true);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    handleGetNutrition();
  }, []);

  const handleClick = async (key: string) => {
    const isSelected = selected.includes(key);

    if (isSelected && selected.length < 2) {
      setModalMsg("영양 목표는 최소 1개 이상 선택해야 합니다.");
      setShowModal(true);
      return;
    }

    if (!isSelected && selected.length >= 3) {
      setModalMsg("특징은 최대 3개까지 선택할 수 있습니다.");
      setShowModal(true);
      return;
    }

    try {
      if (!isSelected) {
        await CrateNutrition(key);
        setSelected((prev) => [...prev, key]);
      } else {
        await DeleteNutrition(key);
        setSelected((prev) => prev.filter((v) => v !== key));
      }
    } catch (err) {
      setModalMsg(formatErrMsg(err));
      setShowModal(true);
    }
  };

  const handleSubmit = () => {
    showToast("영양 목표 변경에 성공했어요.", "success");
    navigate(-1);
  };

  if (isLoading) {
    return <CommonLoading type="data" isLoading={isLoading} />;
  }
  return (
    <div className="my-[30px] px-[20px] w-full flex flex-col flex-1 justify-between gap-y-[20px]">
      <div className="flex flex-col gap-y-[20px]">
        <div className="titleFont">
          영양 목표를 <br />
          선택해주세요
        </div>
        <div className="hintFont]">최대 3개까지 선택할 수 있어요.</div>

        <SelectedGrid
          data={NutritionList}
          selected={selected}
          selectType="nutrition"
          onClick={handleClick}
        />
      </div>

      <CommonBtn
        label="저장"
        onClick={handleSubmit}
        category="green"
        notBottom
      />

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

export default ChangeCustomerNutrition;
