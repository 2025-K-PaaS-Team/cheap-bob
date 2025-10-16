import { CommonBtn, CommonModal } from "@components/common";
import { CommonPrice } from "@components/seller/common";
import type { ProductBase } from "@interface";
import { GetProduct, UpdateProduct } from "@services";
import { useDashboardStore } from "@store";
import { formatErrMsg } from "@utils";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router";

const ChangePackagePrice = () => {
  const repProductId = useDashboardStore((s) => s.repProductId); // string | null
  const [product, setProduct] = useState<ProductBase | null>(null);
  const [loading, setLoading] = useState(true);

  const [showModal, setShowModal] = useState(false);
  const [modalMsg, setModalMsg] = useState("");
  const navigate = useNavigate();

  const load = async (productId: string) => {
    try {
      const res = await GetProduct(productId);
      // 서버 응답이 ProductBase 형태라고 가정
      setProduct(res as ProductBase);
    } catch (err) {
      setModalMsg(formatErrMsg(err));
      setShowModal(true);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (!repProductId) {
      setModalMsg("패키지를 찾을 수 없습니다.");
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

    // (선택) 간단 검증
    if (product.price < 0 || product.sale < 0 || product.sale > product.price) {
      setModalMsg("가격/세일 값을 확인해 주세요.");
      setShowModal(true);
      return;
    }

    try {
      await UpdateProduct(repProductId, {
        ...product,
        price: Math.floor(product.price),
        sale: Math.floor(product.sale),
      });
      navigate(-1);
    } catch (err) {
      setModalMsg(formatErrMsg(err));
      setShowModal(true);
    }
  };

  if (loading) return <div className="mt-[30px] px-[20px]">로딩중…</div>;

  return (
    <div className="mt-[30px] px-[20px] w-full">
      {product && (
        <CommonPrice
          pkg={product}
          setPkg={(next) =>
            setProduct((prev) =>
              typeof next === "function" ? (next as any)(prev) : next
            )
          }
        />
      )}

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

export default ChangePackagePrice;
