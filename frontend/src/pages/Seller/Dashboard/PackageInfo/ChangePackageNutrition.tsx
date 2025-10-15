import { CommonBtn, CommonModal, SelectedGrid } from "@components/common";
import { NutritionList } from "@constant";
import { useDashboardStore } from "@store";
import { DeletePkgNutrition, AddPkgNutrition, GetProduct } from "@services";
import { formatErrMsg } from "@utils";
import type { ProductBase } from "@interface";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router";

const ChangePackageNutrition = () => {
  const navigate = useNavigate();
  const repProductId = useDashboardStore((s) => s.repProductId);

  const [product, setProduct] = useState<ProductBase | null>(null);
  const [selected, setSelected] = useState<string[]>([]);
  const [busyKey, setBusyKey] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  const [showModal, setShowModal] = useState<boolean>(false);
  const [modalMsg, setModalMsg] = useState("");

  const load = async (id: string) => {
    try {
      const res = await GetProduct(id);
      setProduct(res as ProductBase);
      const init = Array.isArray((res as any).nutrition_types)
        ? ((res as any).nutrition_types as string[])
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
    if (!repProductId) {
      setModalMsg("대표 패키지 ID를 찾을 수 없습니다.");
      setShowModal(true);
      setLoading(false);
      return;
    }

    console.log(product);

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
    navigate(-1);
  };

  if (loading) return <div className="mt-[80px] px-[20px]">로딩중…</div>;

  return (
    <div className="mt-[80px] px-[20px] w-full">
      <div className="text-[24px]">패키지의 특징은 무엇인가요?</div>
      <div className="text-[14px] mb-[36px]">
        최대 3개까지 선택할 수 있어요.
      </div>

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

export default ChangePackageNutrition;
