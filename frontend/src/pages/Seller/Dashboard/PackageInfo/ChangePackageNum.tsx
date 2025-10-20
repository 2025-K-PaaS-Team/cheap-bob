import { CommonBtn, CommonModal } from "@components/common";
import { CommonPkgNum } from "@components/seller/common";
import type { ProductRequestType } from "@interface";
import { GetProduct, UpdateProduct } from "@services";
import { useDashboardStore } from "@store";
import { formatErrMsg } from "@utils";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router";

const ChangePackageNum = () => {
  const repProductId = useDashboardStore((s) => s.repProductId);
  const [pkg, setPkg] = useState<ProductRequestType | null>(null);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [modalMsg, setModalMsg] = useState("");

  const navigate = useNavigate();

  const load = async (id: string) => {
    try {
      const res = await GetProduct(id);
      setPkg(res);
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
      setModalMsg("대표 패키지 ID를 찾을 수 없습니다.");
      setShowModal(true);
      setLoading(false);
      return;
    }
    if (!pkg) {
      setModalMsg("패키지 정보를 불러오지 못했습니다.");
      setShowModal(true);
      return;
    }
    const payload: ProductRequestType = {
      ...pkg,
      initial_stock: pkg?.initial_stock,
    };

    try {
      await UpdateProduct(repProductId, payload);
      navigate(-1);
    } catch (err) {
      setModalMsg(formatErrMsg(err));
      setShowModal(true);
    }
  };

  if (loading) return <div className="mt-[30px] px-[20px]">로딩중…</div>;

  return (
    <div className="flex flex-col flex-1 my-[30px] px-[20px] gap-y-[40px]">
      <div className="flex-1 flex">
        {pkg && (
          <CommonPkgNum
            pkg={pkg}
            setPkg={(next) =>
              setPkg((prev) =>
                typeof next === "function" ? (next as any)(prev) : next
              )
            }
          />
        )}
      </div>

      {/* save */}
      <CommonBtn
        label="저장"
        onClick={handleSubmit}
        notBottom
        category="green"
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

export default ChangePackageNum;
