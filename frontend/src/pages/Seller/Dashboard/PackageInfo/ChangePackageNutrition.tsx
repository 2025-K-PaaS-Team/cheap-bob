import { CommonBtn, CommonModal, SelectedGrid } from "@components/common";
import { NutritionList } from "@constant";
import { useDashboardStore } from "@store";
import { DeletePkgNutrition, AddPkgNutrition, GetProduct } from "@services";
import { formatErrMsg } from "@utils";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import CommonLoading from "@components/common/CommonLoading";
import { useToast } from "@context";

const ChangePackageNutrition = () => {
  const { showToast } = useToast();
  const navigate = useNavigate();
  const repProductId = useDashboardStore((s) => s.repProductId);

  const [selected, setSelected] = useState<string[]>([]);
  const [busyKey, setBusyKey] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  const [showModal, setShowModal] = useState<boolean>(false);
  const [modalMsg, setModalMsg] = useState("");

  const load = async (id: string) => {
    try {
      const res = await GetProduct(id);
      const init = Array.isArray((res as any).nutrition_types)
        ? ((res as any).nutrition_types as string[])
        : [];
      setSelected(init);
    } catch (err) {
      setModalMsg(formatErrMsg(err));
      setShowModal(true);
      navigate(-1);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (!repProductId) {
      setModalMsg("대표 패키지 ID를 찾을 수 없습니다.");
      setShowModal(true);
      setIsLoading(false);
      navigate(-1);
      return;
    }

    load(repProductId);
  }, [repProductId]);

  const ensureId = (): string | null => {
    if (!repProductId) {
      setModalMsg("대표 패키지 ID를 찾을 수 없습니다.");
      setShowModal(true);
      return null;
    }
    return repProductId;
  };

  const handleClick = async (key: string) => {
    const productId = ensureId();
    if (!productId || busyKey) return;

    const isSelected = selected.includes(key);

    if (isSelected && selected.length < 2) {
      setModalMsg("특징은 최소 1개 이상 선택해야 합니다.");
      setShowModal(true);
      return;
    }

    // 최대 3개 제한 (추가 시에만 체크)
    if (!isSelected && selected.length >= 3) {
      setModalMsg("특징은 최대 3개까지 선택할 수 있습니다.");
      setShowModal(true);
      return;
    }

    setBusyKey(key);
    try {
      if (isSelected) {
        await DeletePkgNutrition(productId, [key]);
        setSelected((prev) => prev.filter((v) => v !== key));
      } else {
        await AddPkgNutrition(productId, [key]);
        setSelected((prev) => [...prev, key]);
      }
    } catch (err) {
      setModalMsg(formatErrMsg(err));
      setShowModal(true);
    } finally {
      setBusyKey(null);
    }
  };

  const handleSubmit = () => {
    showToast("패키지 영양목표 변경에 성공했어요.", "success");
    navigate(-1);
  };

  if (isLoading) {
    return <CommonLoading type="data" isLoading={isLoading} />;
  }
  return (
    <div className="my-[30px] px-[20px] w-full flex flex-col flex-1 gap-y-[20px]">
      <div className="flex flex-1 flex-col gap-y-[20px]">
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
      </div>

      <CommonBtn
        label="저장"
        onClick={handleSubmit}
        notBottom
        category="green"
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

export default ChangePackageNutrition;
