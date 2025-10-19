import { CommonBtn, CommonModal } from "@components/common";
import type { ProductBase } from "@interface";
import { GetProduct, UpdateProduct } from "@services";
import { useDashboardStore } from "@store";
import { formatErrMsg, validateLength } from "@utils";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router";

const ChangePackageDesc = () => {
  const navigate = useNavigate();
  const repProductId = useDashboardStore((s) => s.repProductId);
  const [product, setProduct] = useState<ProductBase | null>(null);
  const [desc, setDesc] = useState("");
  const [loading, setLoading] = useState(true);

  const [showModal, setShowModal] = useState(false);
  const [modalMsg, setModalMsg] = useState("");

  const load = async (id: string) => {
    try {
      const res = await GetProduct(id);
      setProduct(res as ProductBase);
      setDesc((res as any).description ?? "");
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
    load(repProductId);
  }, [repProductId]);

  const handleSubmit = async () => {
    if (!repProductId) {
      setModalMsg("대표 패키지 ID가 없습니다.");
      setShowModal(true);
      return;
    }
    if (!product) {
      setModalMsg("패키지 정보를 불러오지 못했습니다.");
      setShowModal(true);
      return;
    }
    if (!validateLength(desc.trim(), 1, 100)) {
      setModalMsg("패키지 설명은 1~100자여야 합니다.");
      setShowModal(true);
      return;
    }

    const payload: ProductBase = {
      ...product,
      description: desc.trim(),
    };

    try {
      await UpdateProduct(repProductId, payload);
      navigate(-1);
    } catch (err) {
      setModalMsg(formatErrMsg(err));
      setShowModal(true);
    } finally {
    }
  };

  if (loading) return <div className="mt-[30px] px-[20px]">로딩중...</div>;

  return (
    <div className="mt-[30px] px-[20px] w-full">
      <div className="titleFont">
        변경할 <span className="font-bold">패키지의 설명</span>을 <br /> 입력해
        주세요.
      </div>

      <textarea
        className="w-full h-[140px] bg-custom-white text-[16px] mt-[40px] p-3 rounded"
        placeholder="패키지의 설명을 입력해 주세요"
        value={desc}
        onChange={(e) => setDesc(e.target.value)}
        maxLength={200}
      />

      <CommonBtn label={"저장"} onClick={handleSubmit} category="green" />

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

export default ChangePackageDesc;
