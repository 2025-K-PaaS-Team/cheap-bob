import { CommonBtn, CommonModal, SelectedGrid } from "@components/common";
import { NutritionList } from "@constant";
import { CrateNutrition, DeleteNutrition, GetNutrition } from "@services";
import { formatErrMsg } from "@utils";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router";

const ChangeCustomerMenu = () => {
  const navigate = useNavigate();
  const [selected, setSelected] = useState<string[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

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
      setLoading(false);
    }
  };

  useEffect(() => {
    handleGetNutrition();
  }, []);

  const handleClick = async (key: string) => {
    const isSelected = selected.includes(key);

    // 최대 3개 제한 (추가 시에만 체크)
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
    navigate(-1);
  };

  if (loading) return <div className="mt-[30px] px-[20px]">로딩중…</div>;

  return (
    <div className="mt-[30px] px-[20px] w-full flex flex-col gap-y-[20px]">
      <div className="titleFont">
        변경할 <b>패키지의 영양 특징</b>을 <br />
        선택해 주세요.
      </div>
      <div className="hintFont]">최대 3개까지 선택할 수 있어요.</div>

      <SelectedGrid
        data={NutritionList}
        selected={selected}
        selectType="nutrition"
        onClick={handleClick}
      />

      <CommonBtn label="저장" onClick={handleSubmit} category="green" />

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

export default ChangeCustomerMenu;
